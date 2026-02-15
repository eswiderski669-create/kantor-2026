import requests

def pobierz_kurs(waluta):
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{waluta}/?format=json"
    try:
        
        response = requests.get(url, timeout=5)
        response.raise_for_status() 
        dane = response.json()
        
        kurs = dane["rates"][0]["mid"]
        return float(kurs)
        
    except requests.exceptions.HTTPError:
        print(f"Błąd: Nie znaleziono waluty '{waluta}'.")
        return None
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return None