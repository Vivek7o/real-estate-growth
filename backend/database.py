import sqlite3

def create_database():
    conn = sqlite3.connect('realestate.db')
    cursor = conn.cursor()

    # Table for municipal declarations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipal_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            city TEXT,
            project_type TEXT,
            description TEXT,
            declared_date TEXT,
            latitude REAL,
            longitude REAL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for real estate listings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listing_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            city TEXT,
            property_type TEXT,
            price_per_sqft REAL,
            rental_yield REAL,
            listing_count INTEGER,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for growth scores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS growth_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            city TEXT,
            municipal_score REAL,
            market_score REAL,
            trend_score REAL,
            final_growth_score REAL,
            latitude REAL,
            longitude REAL,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully.")

if __name__ == "__main__":
    create_database()
