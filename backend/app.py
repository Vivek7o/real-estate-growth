from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import sys

# Add backend folder to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from scrapers.municipal_scraper  import scrape_municipal_projects, save_municipal_data
from scrapers.realestate_scraper import scrape_99acres, save_listing_data
from models.growth_score         import calculate_growth_score

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'realestate.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── GET all growth scores for map display ────────────────────────────
@app.route("/api/growth-scores", methods=["GET"])
def get_growth_scores():
    conn = get_db()
    scores = conn.execute(
        "SELECT * FROM growth_scores ORDER BY final_growth_score DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(s) for s in scores])


# ── GET all municipal data ───────────────────────────────────────────
@app.route("/api/municipal", methods=["GET"])
def get_municipal():
    conn = get_db()
    data = conn.execute("SELECT * FROM municipal_data").fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])


# ── GET all listing data ─────────────────────────────────────────────
@app.route("/api/listings", methods=["GET"])
def get_listings():
    conn = get_db()
    data = conn.execute("SELECT * FROM listing_data").fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])


# ── GET top N zones by growth score ─────────────────────────────────
@app.route("/api/top-zones", methods=["GET"])
def get_top_zones():
    limit = request.args.get("limit", 5)
    conn = get_db()
    data = conn.execute(
        "SELECT * FROM growth_scores ORDER BY final_growth_score DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])


# ── GET dashboard summary stats ──────────────────────────────────────
@app.route("/api/summary", methods=["GET"])
def get_summary():
    conn = get_db()

    total_zones     = conn.execute("SELECT COUNT(*) FROM growth_scores").fetchone()[0]
    total_municipal = conn.execute("SELECT COUNT(*) FROM municipal_data").fetchone()[0]
    total_listings  = conn.execute("SELECT COUNT(*) FROM listing_data").fetchone()[0]
    avg_score_row   = conn.execute("SELECT AVG(final_growth_score) FROM growth_scores").fetchone()
    avg_score       = avg_score_row[0] if avg_score_row[0] else 0
    top_zone        = conn.execute(
        "SELECT zone, final_growth_score FROM growth_scores ORDER BY final_growth_score DESC LIMIT 1"
    ).fetchone()

    conn.close()

    return jsonify({
        "total_zones":       total_zones,
        "municipal_records": total_municipal,
        "listing_records":   total_listings,
        "average_score":     round(avg_score, 2),
        "top_zone":          dict(top_zone) if top_zone else {}
    })


# ── POST refresh all data and recalculate scores ─────────────────────
@app.route("/api/refresh", methods=["POST"])
def refresh_data():
    try:
        body = request.get_json() or {}
        city = body.get("city", "Delhi")

        # Step 1: Scrape municipal data
        print(f"Scraping municipal data for {city}...")
        municipal = scrape_municipal_projects(city=city)
        save_municipal_data(municipal)

        # Step 2: Scrape real estate listings
        zones = ["dwarka", "noida", "gurugram", "faridabad", "rohini", "greater noida west"]
        for zone in zones:
            print(f"Scraping listings for {zone}...")
            listings = scrape_99acres(city=city.lower(), zone=zone)
            save_listing_data(listings)

        # Step 3: Recalculate growth scores
        print("Calculating growth scores...")
        scores = calculate_growth_score()

        return jsonify({
            "status":  "success",
            "message": f"Data refreshed successfully. {len(scores)} zones scored.",
            "zones":   len(scores)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Health check ─────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Server is running"})


def initialize():
    """Create database and load sample data if empty."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'realestate.db')
    
    # Create tables if not exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS municipal_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone TEXT, city TEXT, project_type TEXT,
        description TEXT, declared_date TEXT,
        latitude REAL, longitude REAL,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS listing_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone TEXT, city TEXT, property_type TEXT,
        price_per_sqft REAL, rental_yield REAL,
        listing_count INTEGER,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS growth_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone TEXT, city TEXT, municipal_score REAL,
        market_score REAL, trend_score REAL,
        final_growth_score REAL, latitude REAL, longitude REAL,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

    # Load sample data if empty
    count = cursor.execute("SELECT COUNT(*) FROM municipal_data").fetchone()[0]
    if count == 0:
        sample_municipal = [
            ("Dwarka Sector 21","Delhi","Metro Extension","New metro line extension","2024-01-15",28.5530,77.0588),
            ("Noida Sector 62","Delhi","Road Widening","6-lane expressway widening","2024-02-10",28.6270,77.3720),
            ("Gurugram Sector 56","Delhi","Sewage Expansion","New sewage treatment plant","2024-03-05",28.4089,77.0926),
            ("Faridabad Sector 85","Delhi","Industrial Zone","New industrial zone CLU","2024-03-20",28.4082,77.3178),
            ("Rohini Sector 24","Delhi","School/Hospital","New government hospital","2024-04-01",28.7201,77.1025),
            ("Greater Noida West","Delhi","Metro Extension","Aqua line metro extension","2024-04-15",28.5983,77.4280),
        ]
        cursor.executemany(
            "INSERT INTO municipal_data (zone,city,project_type,description,declared_date,latitude,longitude) VALUES (?,?,?,?,?,?,?)",
            sample_municipal
        )

        sample_listings = [
            ("Dwarka Sector 21","Delhi","Residential",7500,2.8,145),
            ("Noida Sector 62","Delhi","Residential",5200,3.2,210),
            ("Gurugram Sector 56","Delhi","Residential",9800,2.5,320),
            ("Faridabad Sector 85","Delhi","Residential",4100,3.8,89),
            ("Rohini Sector 24","Delhi","Residential",6200,3.0,175),
            ("Greater Noida West","Delhi","Residential",4800,3.5,260),
        ]
        cursor.executemany(
            "INSERT INTO listing_data (zone,city,property_type,price_per_sqft,rental_yield,listing_count) VALUES (?,?,?,?,?,?)",
            sample_listings
        )
        conn.commit()
        print("Sample data loaded.")

    conn.close()

    # Calculate initial scores
    try:
        from models.growth_score import calculate_growth_score
        calculate_growth_score()
        print("Growth scores calculated.")
    except Exception as e:
        print(f"Score calculation error: {e}")


# Run initialization then start server
initialize()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)