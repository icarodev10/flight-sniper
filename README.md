# ✈️ Flight Sniper Pro - Intelligent RPA for Airfare Monitoring

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-Undetected-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)

> **Watch the Demo:** 👇
>
> https://github.com/user-attachments/assets/a5f3d705-37aa-4189-9de3-733ee93d1e7e

## 📋 About the Project

**Flight Sniper Pro** is an advanced **RPA (Robotic Process Automation)** tool designed to solve a real-world problem: finding the best time to buy flight tickets without constant manual checking.

Unlike simple scrapers, this bot uses **computer vision techniques (Regex)** and **anti-detection algorithms** to navigate dynamic Google Flights pages, extract hidden data, and calculate historical averages to identify *true* discounts.

**Key Highlight:** The system features a "Stealth Mode" to bypass bot detection (Cloudflare/Google) and integrates a full-stack flow: **Scraping (Backend) ➡️ Database (SQLite) ➡️ Analytics (Frontend) ➡️ Notification (Email).**

## 🚀 Key Features

* **🕵️‍♂️ Stealth Mode Automation:** Uses `undetected-chromedriver` to mimic human behavior and avoid IP blocks/CAPTCHAs.
* **🧠 Market Intelligence:** Calculates the **Historical Average** of the route. It doesn't just show the price; it tells you if it's cheap compared to the past.
* **📧 Smart Alerts:** Automatically sends an email notification when a "Super Promo" (price 20% below average) is found.
* **⚡ Actionable Dashboard:** A Streamlit interface with real-time logs, progress bars, and **Direct Purchase Links** deep-linked to the airline's offer.
* **📊 Data Persistence:** All data is saved in a local SQLite database for long-term trend analysis.

## 🛠️ Tech Stack

* **Core:** Python 3.11+
* **Automation:** Selenium WebDriver & Undetected-Chromedriver
* **Data Engineering:** Pandas (ETL) & SQLite (Storage)
* **Regex:** Advanced text pattern extraction (Time/Currency)
* **Frontend:** Streamlit (Reactive Dashboard with CSS injection)
* **DevOps:** Environment Variables (`.env`) for credential security.

## 📦 How to Run

1.  **Clone the repository:**

    git clone [https://github.com/icarodev10/flight-sniper.git](https://github.com/icarodev10/flight-sniper.git)
    cd flight-sniper


2.  **Install dependencies:**

    pip install -r requirements.txt


3.  **Configure Credentials:**
    * Rename `.env.example` to `.env`.
    * Add your email credentials (required for alerts).

4.  **Run the App:**

    streamlit run dashboard.py

    The application will open in your browser at `http://localhost:8501`.

## 📂 Project Structure

flight-sniper/

├── dashboard.py       # Frontend: UI, Charts, and Control Logic

├── robo_voos.py       # Backend: The Scraper Core & Email Logic

├── meus_voos.db       # Database (Created automatically)

├── requirements.txt   # Project dependencies

├── .env.example       # Security template

└── README.md          # Documentation

⚠️ Disclaimer
This software was developed strictly for educational purposes, focusing on learning programming logic, task automation, and data engineering. The developer is not responsible for any misuse of this tool.

Developed by Icaro de Souza de Lima Python Developer & RPA Enthusiast

ℹ️ Note: The source code comments and User Interface are currently in Portuguese (PT-BR), designed for the Brazilian market context.
