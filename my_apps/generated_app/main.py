#!/usr/bin/env python3
import sys
import subprocess
import webbrowser
from urllib.parse import quote_plus

def open_youtube(search_term: str):
    query = quote_plus(search_term)
    url = f"https://www.youtube.com/results?search_query={query}"
    # Intentar abrir con termux-open-url (mejor en Termux/Android)
    try:
        subprocess.run(["termux-open-url", url], check=True)
        return
    except Exception:
        pass
    # Si no está termux-open-url, intentar con webbrowser de Python
    try:
        webbrowser.open(url)
    except Exception as e:
        print("No se pudo abrir el navegador automáticamente:", e)
        print("URL:", url)

if __name__ == "__main__":
    # Si se pasa argumento, usarlo como búsqueda; si no, buscar 'smell like teen spirit'
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
    else:
        term = "smell like teen spirit"
    open_youtube(term)