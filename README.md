# Real Estate Growth Dashboard
## Predictive Urban Growth Modeling — Problem Statement 3

---

## How to Run in VS Code

### Step 1 — Open Project in VS Code
1. Open VS Code
2. Click File > Open Folder
3. Select the `real-estate-growth` folder
4. You will see all files in the Explorer on the left

### Step 2 — Open Terminal in VS Code
Press  Ctrl + `  (backtick key)
Or go to Terminal > New Terminal

### Step 3 — Install Python Libraries
Type this in the terminal and press Enter:

    cd backend
    pip install -r requirements.txt

Wait for all libraries to install. This takes 1-2 minutes.

### Step 4 — Run Setup (ONE TIME ONLY)
Still inside the backend folder, run:

    python setup.py

This will:
- Create the database
- Load sample municipal data
- Load sample real estate listings
- Calculate growth scores for all zones
- Print a score ranking in your terminal

### Step 5 — Start the Flask Server
After setup is done, run:

    python app.py

You will see:
    Starting Flask server on http://localhost:5000

Keep this terminal open. Do not close it.

### Step 6 — Open the Frontend
Open a NEW terminal tab (click the + button in terminal)
Then run:

    cd frontend

Option A — Just open the file:
Right click on  frontend/index.html  in VS Code Explorer
Click  Open with Live Server
(Requires the Live Server extension — install it from Extensions tab)

Option B — Open directly in browser:
Find the file at:  real-estate-growth/frontend/index.html
Double click it to open in your browser

### Step 7 — Use the Dashboard
- The map loads with colored heat zones
- Red/orange = high growth potential
- Blue = low growth potential
- Click any dot on the map to see the score breakdown
- Hover over a dot to see a quick tooltip
- Click a zone in the left sidebar to fly to that location
- Click "Refresh Data" to re-scrape and recalculate

---

## API Endpoints (for testing in browser)

    http://localhost:5000/api/health          (check if server is running)
    http://localhost:5000/api/growth-scores   (all zone scores)
    http://localhost:5000/api/summary         (summary statistics)
    http://localhost:5000/api/top-zones?limit=3 (top 3 zones)
    http://localhost:5000/api/municipal       (municipal projects)
    http://localhost:5000/api/listings        (real estate listings)

---

## Project Structure

    real-estate-growth/
    ├── backend/
    │   ├── scrapers/
    │   │   ├── municipal_scraper.py    (scrapes govt project data)
    │   │   └── realestate_scraper.py  (scrapes 99acres listing data)
    │   ├── models/
    │   │   └── growth_score.py        (calculates growth velocity score)
    │   ├── app.py                     (Flask API server)
    │   ├── database.py                (creates SQLite database)
    │   ├── setup.py                   (one-time setup script)
    │   ├── requirements.txt           (Python libraries needed)
    │   └── realestate.db             (created after running setup.py)
    ├── frontend/
    │   ├── index.html                 (main dashboard page)
    │   ├── style.css                  (all styling)
    │   └── map.js                     (map logic and API calls)
    └── data/
        ├── raw/                       (store downloaded raw data here)
        └── processed/                 (store cleaned data here)

---

## Score Formula

    Growth Score = (Municipal Score x 0.50)
                 + (Market Score   x 0.30)
                 + (Trend Score    x 0.20)

    Score >= 70  →  High Growth Zone   (Green)
    Score 40-69  →  Medium Growth Zone (Yellow)
    Score < 40   →  Low Growth Zone    (Red)

---

## VS Code Extensions to Install

Open VS Code Extensions tab (Ctrl+Shift+X) and install:
- Python (by Microsoft)
- Live Server (by Ritwick Dey)
- Pylance (by Microsoft)
