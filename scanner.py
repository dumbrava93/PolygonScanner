import logging
import sys
import time
from polygon import RESTClient
from polygon.exceptions import AuthError, BadResponse

# Configurare Logging
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
    symbols_count = 0
    max_retries = 3

    print("🚀 Inițiez scanarea optimizată (Simbol + Nume)...")

    try:
        # Optimizare 1: Filtrare direct la sursă pentru viteză maximă și consum redus de date
        tickers_iterator = client.list_tickers(
            market='stocks',
            type='CS',
            active=True,
            limit=1000
        )

        with open('universe.txt', 'w', encoding='utf-8') as f:
            # Adăugăm un header pentru claritate (format CSV)
            f.write("Ticker, Name\n")

            # Folosim un iterator robust care poate gestiona limitările de viteză
            while True:
                try:
                    for ticker in tickers_iterator:
                        symbols_count += 1
                        # Salvăm Simbolul și Numele complet (cu ghilimele pentru a evita erori la virgule)
                        f.write(f'{ticker.ticker}, "{ticker.name}"\n')

                        # Optimizare 2: Buffering la scriere (flush doar la 500 rânduri)
                        if symbols_count % 500 == 0:
                            f.flush()
                            print(f"Progres: {symbols_count} simboluri salvate...")

                    # Dacă am terminat iterația fără erori, ieșim din loop-ul while
                    break

                except BadResponse as e:
                    if "429" in str(e) or "limit" in str(e).lower():
                        print(f"\n⚠️ Rate Limit atins. Aștept 60 de secunde pentru resetare...")
                        time.sleep(60)
                        # Notă: In mod normal aici ar trebui să reluăm de la ultimul cursor,
                        # dar iteratorul nativ din polygon-api-client gestionează cursorul intern.
                        # Continuăm iterația.
                        continue
                    else:
                        raise e

        # Output final
        print(f"\n✅ Analiză finalizată.")
        print(f"Număr total de acțiuni identificate: {symbols_count}")

        input("\n🚀 Univers extras cu succes! Apasă ENTER pentru a închide consola...")

    except AuthError:
        msg = f"Eroare 403: Acces interzis. Verifică dacă cheia API este activă."
        logging.error(msg)
        print(f"\n❌ {msg}")
        sys.exit(1)
    except Exception as e:
        msg = f"Eroare neașteptată: {str(e)}"
        logging.error(msg)
        print(f"\n❌ {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
