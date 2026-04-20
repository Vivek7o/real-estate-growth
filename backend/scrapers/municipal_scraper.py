import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_municipal_projects(city="Delhi", url=None):
    """
    Scrapes municipal project declarations.
    Uses sample data for development.
    Replace URL with your target municipal corporation website.
    """
    projects = []

    try:
        if url:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            rows = soup.find_all("tr", class_="tender-row")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    project = {
                        "zone":          cols[0].text.strip(),
                        "city":          city,
                        "project_type":  cols[1].text.strip(),
                        "description":   cols[2].text.strip(),
                        "declared_date": cols[3].text.strip() if len(cols) > 3 else datetime.now().strftime("%Y-%m-%d"),
                        "latitude":      None,
                        "longitude":     None,
                    }
                    projects.append(project)

        if not projects:
            print("Using sample municipal data for development...")
            projects = get_sample_municipal_data(city)

    except Exception as e:
        print(f"Scraping error: {e}")
        projects = get_sample_municipal_data(city)

    return projects


def get_sample_municipal_data(city):
    """
    Sample data used during development and testing.
    Replace with real scraped data in production.
    """
    return [
        {
            "zone":          "Dwarka Sector 21",
            "city":          city,
            "project_type":  "Metro Extension",
            "description":   "New metro line extension connecting Dwarka to IGI Airport",
            "declared_date": "2024-01-15",
            "latitude":      28.5530,
            "longitude":     77.0588
        },
        {
            "zone":          "Noida Sector 62",
            "city":          city,
            "project_type":  "Road Widening",
            "description":   "6-lane expressway widening project approved",
            "declared_date": "2024-02-10",
            "latitude":      28.6270,
            "longitude":     77.3720
        },
        {
            "zone":          "Gurugram Sector 56",
            "city":          city,
            "project_type":  "Sewage Expansion",
            "description":   "New sewage treatment plant and pipeline network approved",
            "declared_date": "2024-03-05",
            "latitude":      28.4089,
            "longitude":     77.0926
        },
        {
            "zone":          "Faridabad Sector 85",
            "city":          city,
            "project_type":  "Industrial Zone",
            "description":   "New industrial zone declared under CLU policy change",
            "declared_date": "2024-03-20",
            "latitude":      28.4082,
            "longitude":     77.3178
        },
        {
            "zone":          "Rohini Sector 24",
            "city":          city,
            "project_type":  "School/Hospital",
            "description":   "New government hospital and school complex under construction",
            "declared_date": "2024-04-01",
            "latitude":      28.7201,
            "longitude":     77.1025
        },
        {
            "zone":          "Greater Noida West",
            "city":          city,
            "project_type":  "Metro Extension",
            "description":   "Aqua line metro extension to Greater Noida West approved",
            "declared_date": "2024-04-15",
            "latitude":      28.5983,
            "longitude":     77.4280
        },
    ]


def save_municipal_data(projects):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'realestate.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for p in projects:
        cursor.execute('''
            INSERT INTO municipal_data
            (zone, city, project_type, description, declared_date, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            p["zone"], p["city"], p["project_type"],
            p["description"], p["declared_date"],
            p["latitude"], p["longitude"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(projects)} municipal records.")


if __name__ == "__main__":
    data = scrape_municipal_projects(city="Delhi")
    save_municipal_data(data)
    print("Municipal scraper done.")
