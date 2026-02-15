from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
import kantor
import baza

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


baza.utworz_tabele()




@app.get("/")  
def strona_domowa():
    return {"wiadomosc": "Witaj w Kantorze 2026!"}

@app.get("/kurs/{waluta}")  
def sprawdz_kurs(waluta: str):
    
    wynik = kantor.pobierz_kurs(waluta)
    
    if wynik is not None:
        return {
            "waluta": waluta.upper(), 
            "kurs": wynik,
            "status": "sukces"
        }
    else:
        return {"blad": "Nie znaleziono waluty"}

@app.get("/kup/{waluta}/{ilosc}") 
def kup_walute(waluta: str, ilosc: float):
    kurs = kantor.pobierz_kurs(waluta)
    
    if kurs:
        koszt = ilosc * kurs
       
        baza.zapisz_transakcje(waluta.upper(), kurs, ilosc)
        
        return {
            "kupiono": f"{ilosc} {waluta.upper()}",
            "koszt_pln": round(koszt, 2),
            "kurs_wymiany": kurs,
            "info": "Zapisano w bazie danych "
        }
    else:
        return {"blad": "Transakcja nieudana"}