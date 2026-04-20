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


if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)
