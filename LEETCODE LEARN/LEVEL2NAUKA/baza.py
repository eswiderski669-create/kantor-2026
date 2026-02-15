import sqlite3
from datetime import datetime

def utworz_tabele():
    polaczenie = sqlite3.connect("kantor.db")
    kursor = polaczenie.cursor()
  
    kursor.execute("""
    CREATE TABLE IF NOT EXISTS historia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        waluta TEXT,
        ilosc REAL,
        kurs REAL,
        data TEXT
    )
    """)
    
    polaczenie.commit()
    polaczenie.close()
    print("Tabela przygotowana.")

def zapisz_transakcje(waluta, kurs, ilosc):

    polaczenie = sqlite3.connect("kantor.db")
    kursor = polaczenie.cursor()

    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = "INSERT INTO historia (waluta, kurs, ilosc, data) VALUES (?, ?, ?, ?)"

    dane = (waluta.upper(), kurs, ilosc, teraz)
    
    try:
        kursor.execute(sql, dane)
        polaczenie.commit()
        print(f" Transakcja {waluta.upper()} zapisana w bazie.")
    except Exception as e:
        print(f" Błąd zapisu do bazy: {e}")
    finally:
        polaczenie.close()

if __name__ == "__main__":
    utworz_tabele()