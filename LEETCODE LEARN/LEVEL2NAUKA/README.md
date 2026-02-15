# 💰 Kantor Walutowy 2026

Prosta aplikacja Fullstack do sprawdzania kursów walut i symulacji zakupu. Projekt pobiera rzeczywiste dane z API Narodowego Banku Polskiego (NBP), oblicza koszt wymiany i zapisuje historię transakcji w bazie danych.

## 🚀 Live Demo
Aplikacja działa w chmurze: **[WKLEJ TUTAJ SWÓJ LINK Z RENDERA]**

## 🛠 Technologie
Projekt zbudowany w oparciu o nowoczesny stack Python:
* **Backend:** Python 3.12, FastAPI
* **Database:** SQLite3 (SQL)
* **Frontend:** HTML5, JavaScript (Fetch API)
* **External API:** NBP Web API


## ⚙️ Funkcjonalności
1.  **Pobieranie Kursów:** Łączy się z zewnętrznym serwisem NBP w czasie rzeczywistym.
2.  **Kalkulator:** Przelicza kwotę zakupu (EUR/USD/CHF) na PLN.
3.  **Architektura:** Podział na moduły (API, Logika biznesowa, Warstwa danych).
4.  **Baza Danych:** Trwały zapis historii transakcji.

## 📦 Jak uruchomić lokalnie?
1. Sklonuj repozytorium:
   `git clone https://github.com/TWOJ-NICK/kantor-2026.git`
2. Zainstaluj zależności:
   `pip install -r requirements.txt`
3. Uruchom serwer:
   `python -m uvicorn api:app --reload`