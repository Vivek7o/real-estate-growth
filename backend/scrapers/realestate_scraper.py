import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_99acres(city="delhi", zone="dwarka"):
    """
    Scrapes price and listing data from 99acres.
    Note: Always check robots.txt before scraping any website.
    Uses sample data during development.
    """
    listings = []

    try:
        url = f"https://www.99acres.com/property-for-sale-in-{zone}-{city}-ffid"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        cards = soup.find_all("div", class_="srpTuple__tileContainer")

        for card in cards:
            try:
                price_tag = card.find("span", class_="srpTuple__priceLabel")
                area_tag  = card.find("span", class_="srpTuple__areaConfig")
                type_tag  = card.find("span", class_="srpTuple__propType")

                price_text = price_tag.text.strip() if price_tag else "0"
                area_text  = area_tag.text.strip()  if area_tag  else "0"

                listing = {
                    "zone":          zone.title(),
                    "city":          city.title(),
                    "property_type": type_tag.text.strip() if type_tag else "Residential",
                    "price_per_sqft":parse_price(price_text, area_text),
                    "rental_yield":  0.0,
                    "listing_count": 1,
                }
                listings.append(listing)
            except Exception:
                continue

        if not listings:
            print(f"No listings found for {zone}, using sample data...")
            listings = get_sample_listing_data(city, zone)

    except Exception as e:
        print(f"Scraping error for {zone}: {e}")
        listings = get_sample_listing_data(city, zone)

    return listings


def parse_price(price_text, area_text):
    """Convert price string like 45 Lac and area 850 sqft to price per sqft."""
    try:
        price_num = float(''.join(filter(str.isdigit, price_text.split()[0])))
        if "Lac" in price_text or "lac" in price_text:
            price_num *= 100000
        elif "Cr" in price_text or "cr" in price_text:
            price_num *= 10000000

        area_num = float(''.join(filter(str.isdigit, area_text.split()[0])))
        return round(price_num / area_num, 2) if area_num > 0 else 0
    except Exception:
        return 0.0


def get_sample_listing_data(city, zone):
    """
    Sample listing data used during development.
    Replace with real scraped data in production.
    """
    samples = {
        "dwarka":        {"price_per_sqft": 7500,  "rental_yield": 2.8, "listing_count": 145},
        "noida":         {"price_per_sqft": 5200,  "rental_yield": 3.2, "listing_count": 210},
        "gurugram":      {"price_per_sqft": 9800,  "rental_yield": 2.5, "listing_count": 320},
        "faridabad":     {"price_per_sqft": 4100,  "rental_yield": 3.8, "listing_count": 89},
        "rohini":        {"price_per_sqft": 6200,  "rental_yield": 3.0, "listing_count": 175},
        "greater noida west": {"price_per_sqft": 4800, "rental_yield": 3.5, "listing_count": 260},
    }

    key = zone.lower()
    data = samples.get(key, {"price_per_sqft": 5000, "rental_yield": 3.0, "listing_count": 100})

    return [{
        "zone":          zone.title(),
        "city":          city.title(),
        "property_type": "Residential",
        "price_per_sqft":data["price_per_sqft"],
        "rental_yield":  data["rental_yield"],
        "listing_count": data["listing_count"],
    }]


def save_listing_data(listings):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'realestate.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for item in listings:
        cursor.execute('''
            INSERT INTO listing_data
            (zone, city, property_type, price_per_sqft, rental_yield, listing_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            item["zone"], item["city"], item["property_type"],
            item["price_per_sqft"], item["rental_yield"],
            item["listing_count"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(listings)} listing records for {listings[0]['zone'] if listings else 'unknown'}.")


if __name__ == "__main__":
    zones = ["dwarka", "noida", "gurugram", "faridabad", "rohini", "greater noida west"]
    for zone in zones:
        data = scrape_99acres(city="delhi", zone=zone)
        save_listing_data(data)
        time.sleep(2)
    print("Real estate scraper done.")
