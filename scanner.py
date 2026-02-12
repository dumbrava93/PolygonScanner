import os
import logging
import sys
import json
from polygon import RESTClient
from polygon.exceptions import AuthError, BadResponse

# Configurare Logging conform specificațiilor
logging.basicConfig(
    filename='scanner_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Obținerea cheii API din variabilele de mediu
    api_key = os.getenv('POLYGON_API_KEY') or os.getenv('PolyGon_Key')
    if not api_key:
        error_msg = "Eroare: Variabila de mediu POLYGON_API_KEY sau PolyGon_Key nu este setată."
        print(error_msg)
        logging.error(f"{error_msg} (Simboluri deja adăugate: 0)")
        return

    # Inițializare client Polygon
    client = RESTClient(api_key)
    symbols_count = 0

    try:
        # 1. Funcția API: client.list_tickers()
        # 2. Parametri de filtrare: market='stocks', type='CS', active=True, limit=1000
        # 3. Paginare: Utilizăm iteratorul nativ
        tickers_iterator = client.list_tickers(
            market='stocks',
            type='CS',
            active=True,
            limit=1000
        )

        # Îmbunătățire 1: Scriere incrementală în universe.txt
        with open('universe.txt', 'w') as f:
            for ticker in tickers_iterator:
                symbols_count += 1
                f.write(f"{ticker.ticker}\n")
                f.flush()  # Asigură scrierea imediată pe disc

                # Îmbunătățire 2: Update în consolă la fiecare 500 de simboluri
                if symbols_count % 500 == 0:
                    print(f"Progres: {symbols_count} simboluri identificate...")

        # 5. Output final: Afișare total
        print(f"Număr total de acțiuni identificate: {symbols_count}")

    except AuthError:
        msg = f"Eroare 403: Acces interzis. Verifică dacă cheia API este activă sau dacă planul Starter permite acest endpoint. (Simboluri deja adăugate: {symbols_count})"
        logging.error(msg)
        print(msg)
        sys.exit(1)
    except BadResponse as e:
        error_str = str(e)
        is_rate_limit = "limit" in error_str.lower() or "429" in error_str
        is_forbidden = any(term in error_str.lower() for term in ["unauthorized", "forbidden", "permission", "plan", "unknown api key"])

        if is_rate_limit:
            msg = f"Eroare 429: Limitare de viteză (Rate Limit). Scriptul va aștepta înainte de a reîncerca. (Simboluri deja adăugate: {symbols_count})"
        elif is_forbidden:
            msg = f"Eroare 403: Acces interzis. Verifică dacă cheia API este activă sau dacă planul Starter permite acest endpoint. (Simboluri deja adăugate: {symbols_count})"
        else:
            msg = f"Eroare de la API (Bad Response): {error_str}. (Simboluri deja adăugate: {symbols_count})"

        logging.error(msg)
        print(msg)
        sys.exit(1)
    except Exception as e:
        msg = f"Eroare neașteptată: {str(e)}. (Simboluri deja adăugate: {symbols_count})"
        logging.error(msg)
        print(msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
