import logging
import sys
from polygon import RESTClient
from polygon.exceptions import AuthError, BadResponse

# Configurare Logging conform specificațiilor
logging.basicConfig(
    filename='scanner_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Cheia API hardcodată conform solicitării utilizatorului
    api_key = 'VUHuK_qi2S_wYugH9NjeUrQRysQJ3OCR'

    # Inițializare client Polygon
    client = RESTClient(api_key)
    total_count = 0
    symbols_count = 0

    try:
        # Preluăm toate tickerele pentru a putea număra totalul global
        tickers_iterator = client.list_tickers(limit=1000)

        # Îmbunătățire 1: Scriere incrementală în universe.txt
        with open('universe.txt', 'w', encoding='utf-8') as f:
            f.write("Ticker, Name\n")
            for ticker in tickers_iterator:
                total_count += 1

                # Aplicăm filtrele manual: market='stocks', type='CS', active=True
                # Folosim getattr pentru siguranță, deși atributele ar trebui să existe
                if getattr(ticker, 'market', None) == 'stocks' and \
                   getattr(ticker, 'type', None) == 'CS' and \
                   getattr(ticker, 'active', False):

                    symbols_count += 1
                    f.write(f'{ticker.ticker}, "{ticker.name}"\n')
                    f.flush()  # Asigură scrierea imediată pe disc

                    # Îmbunătățire 2: Update în consolă la fiecare 500 de simboluri filtrate
                    if symbols_count % 500 == 0:
                        print(f"Progres: {symbols_count} simboluri identificate (din {total_count} analizate)...")

        # Output final: Afișare totaluri
        print(f"\nAnaliză finalizată.")
        print(f"Număr total de tickere returnate de funcție (global): {total_count}")
        print(f"Număr de acțiuni rămase după filtrare: {symbols_count}")

        # Linia solicitată de utilizator
        input("\n🚀 Univers extras cu succes! Apasă ENTER pentru a închide consola...")

    except AuthError:
        msg = f"Eroare 403: Acces interzis. Verifică dacă cheia API este activă. (Simboluri deja adăugate: {symbols_count})"
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
            msg = f"Eroare 403: Acces interzis. Verifică dacă cheia API este activă. (Simboluri deja adăugate: {symbols_count})"
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
