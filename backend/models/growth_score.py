import sqlite3
import pandas as pd
import os

def calculate_growth_score():
    """
    Growth Velocity Score Formula:

    Final Score = (Municipal Score x 0.50) +
                  (Market Score   x 0.30) +
                  (Trend Score    x 0.20)

    Why these weights:
    - Municipal declarations are LEAD indicators (most predictive)  -> 50%
    - Market activity shows CURRENT demand                          -> 30%
    - Price trend shows MOMENTUM                                    -> 20%
    """

    db_path = os.path.join(os.path.dirname(__file__), '..', 'realestate.db')
    conn = sqlite3.connect(db_path)

    municipal_df = pd.read_sql("SELECT * FROM municipal_data", conn)
    listing_df   = pd.read_sql("SELECT * FROM listing_data",   conn)
    conn.close()

    results = []

    all_zones = set(municipal_df["zone"].tolist() + listing_df["zone"].tolist())

    for zone in all_zones:

        m_data = municipal_df[municipal_df["zone"] == zone]
        l_data = listing_df[listing_df["zone"] == zone]

        # ── MUNICIPAL SCORE (0 to 100) ──────────────────────────────
        project_weights = {
            "Metro Extension":   30,
            "Road Widening":     20,
            "Sewage Expansion":  15,
            "Industrial Zone":   25,
            "School/Hospital":   10,
        }

        municipal_score = 0
        for _, row in m_data.iterrows():
            weight = project_weights.get(row["project_type"], 10)
            municipal_score += weight

        municipal_score = min(municipal_score, 100)

        # ── MARKET SCORE (0 to 100) ──────────────────────────────────
        if not l_data.empty:
            avg_price      = l_data["price_per_sqft"].mean()
            total_listings = l_data["listing_count"].sum()

            price_score   = min((avg_price / 15000) * 100, 100)
            density_score = min((total_listings / 500) * 100, 100)
            market_score  = (price_score * 0.6) + (density_score * 0.4)
        else:
            market_score = 0

        # ── TREND SCORE (0 to 100) ───────────────────────────────────
        if not l_data.empty:
            avg_rental_yield = l_data["rental_yield"].mean()
            # Low rental yield means prices rose faster than rent
            # which is a sign of strong capital appreciation
            trend_score = max(0, 100 - (avg_rental_yield * 15))
        else:
            trend_score = 0

        # ── FINAL GROWTH VELOCITY SCORE ─────────────────────────────
        final_score = (
            (municipal_score * 0.50) +
            (market_score    * 0.30) +
            (trend_score     * 0.20)
        )

        lat = m_data["latitude"].iloc[0]  if not m_data.empty else 28.6139
        lon = m_data["longitude"].iloc[0] if not m_data.empty else 77.2090

        results.append({
            "zone":               zone,
            "city":               m_data["city"].iloc[0] if not m_data.empty else "Delhi",
            "municipal_score":    round(municipal_score, 2),
            "market_score":       round(market_score,    2),
            "trend_score":        round(trend_score,     2),
            "final_growth_score": round(final_score,     2),
            "latitude":           lat,
            "longitude":          lon,
        })

    save_growth_scores(results)
    return results


def save_growth_scores(scores):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'realestate.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM growth_scores")

    for s in scores:
        cursor.execute('''
            INSERT INTO growth_scores
            (zone, city, municipal_score, market_score,
             trend_score, final_growth_score, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            s["zone"], s["city"],
            s["municipal_score"], s["market_score"],
            s["trend_score"], s["final_growth_score"],
            s["latitude"], s["longitude"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved growth scores for {len(scores)} zones.")


if __name__ == "__main__":
    scores = calculate_growth_score()
    print("\nGrowth Scores:")
    print("-" * 50)
    for s in sorted(scores, key=lambda x: x["final_growth_score"], reverse=True):
        print(f"{s['zone']:<30} Score: {s['final_growth_score']}")
