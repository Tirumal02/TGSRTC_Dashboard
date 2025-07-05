# TGSRTC OPRS Dashboard

A Streamlit web dashboard for visualizing **TGSRTC OPRS and NON-OPRS** passenger data. It supports month-wise and stage-wise passenger summaries using CSV files organized by month.

## Features

- 📅 Filter data by date range
- 🚌 Select booking type: OPRS / NON-OPRS / BOTH
- 🏙️ Filter by boarding & destination cities/stages
- 📊 Visualize passenger totals and trends
- 📈 Line charts for passenger movement over time
- 📌 Stage-wise pivot tables

---

## Folder Structure

project/
│
├── dashboard.py
├── LOGO.png
├── Cities.csv
└── Monthwise Files/
├── Apr_2024.csv
├── May_2024.csv
└── ...


- **Monthwise Files/**: Contains monthly passenger data CSVs.
- **Cities.csv**: List of boarding cities (must have column `PAX_CITIES`).
- **LOGO.png**: Logo for the dashboard header.

---

## Installation

### Python 3.7+

### Dependencies

Install required libraries:

```bash
pip install streamlit pandas


