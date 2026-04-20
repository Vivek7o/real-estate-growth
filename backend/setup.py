"""
setup.py
Run this ONE TIME to set up the entire project.
It creates the database and loads sample data automatically.
"""

import sys
import os

# Make sure we are running from the backend folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("  Real Estate Growth Dashboard — Setup")
print("=" * 50)

# Step 1: Create database
print("\nStep 1: Creating database...")
from database import create_database
create_database()

# Step 2: Load municipal data
print("\nStep 2: Loading municipal data...")
from scrapers.municipal_scraper import scrape_municipal_projects, save_municipal_data
municipal_data = scrape_municipal_projects(city="Delhi")
save_municipal_data(municipal_data)

# Step 3: Load listing data
print("\nStep 3: Loading real estate listing data...")
from scrapers.realestate_scraper import scrape_99acres, save_listing_data
import time

zones = ["dwarka", "noida", "gurugram", "faridabad", "rohini", "greater noida west"]
for zone in zones:
    listings = scrape_99acres(city="delhi", zone=zone)
    save_listing_data(listings)
    time.sleep(1)

# Step 4: Calculate growth scores
print("\nStep 4: Calculating growth scores...")
from models.growth_score import calculate_growth_score
scores = calculate_growth_score()

print("\n" + "=" * 50)
print("  Setup Complete!")
print("=" * 50)
print(f"\nZones scored: {len(scores)}")
print("\nGrowth Score Rankings:")
print("-" * 45)
for s in sorted(scores, key=lambda x: x["final_growth_score"], reverse=True):
    bar_len = int(s["final_growth_score"] / 5)
    bar = "#" * bar_len
    print(f"{s['zone']:<25} {s['final_growth_score']:>6}  {bar}")

print("\nNext step: Run  python app.py  to start the server")
print("Then open:  frontend/index.html  in your browser")
