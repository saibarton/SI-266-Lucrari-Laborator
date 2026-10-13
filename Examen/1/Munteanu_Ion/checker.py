import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Creeaza adresa completa a unui site."""
    if path.startswith("/"):
        return "https://" + host + path
    else:
        return "https://" + host + "/" + path


def is_https(url):
    """Verifica daca adresa incepe cu https://."""
    if url.startswith("https://"):
        return True
    else:
        return False


def show_response(url):
    """Afiseaza statusul si tipul continutului."""
    try:
        raspuns = requests.get(url, timeout=5)
        print("Status:", raspuns.status_code)
        print("Content-Type:", raspuns.headers.get("Content-Type", "unknown"))
    except requests.exceptions.RequestException:
        print("Eroare: site-ul nu poate fi accesat")


def check_site(url):
    """Returneaza informatii despre un site."""
    try:
        raspuns = requests.get(url, timeout=5)
        rezultat = {
            "status": raspuns.status_code,
            "content_type": raspuns.headers.get("Content-Type", "unknown"),
            "length": len(raspuns.content),
            "server": raspuns.headers.get("Server", "unknown")
        }
        return rezultat
    except requests.exceptions.RequestException:
        return {"status": None, "error": "Site inaccesibil"}


def scan_sites():
    """Verifica lista de site-uri si afiseaza doar cele cu status 200."""
    rezultate = []
    reusite = []

    for url in SITES:
        rezultat = check_site(url)
        rezultate.append(rezultat)

        if rezultat["status"] == 200:
            reusite.append({"url": url, "length": rezultat["length"]})

    # Sortare de la cel mai mare la cel mai mic
    for i in range(len(reusite)):
        for j in range(i + 1, len(reusite)):
            if reusite[i]["length"] < reusite[j]["length"]:
                aux = reusite[i]
                reusite[i] = reusite[j]
                reusite[j] = aux

    for site in reusite:
        print(site["url"], "-> 200,", site["length"], "octeti")

    print("Reusite:", len(reusite), "| Esuate:", len(rezultate) - len(reusite))


def check_headers(url):
    """Verifica cele patru antete de securitate."""
    try:
        raspuns = requests.get(url, timeout=5)
        prezente = []
        lipsa = []

        for antet in SECURITY_HEADERS:
            gasit = False
            for nume in raspuns.headers:
                if nume.lower() == antet.lower():
                    gasit = True

            if gasit:
                prezente.append(antet)
            else:
                lipsa.append(antet)

        scor = len(prezente) * 100 // len(SECURITY_HEADERS)
        return {"present": prezente, "missing": lipsa, "score": scor}
    except requests.exceptions.RequestException:
        return {"status": None, "error": "Site inaccesibil"}


def retry_check(url, attempts=3):
    """Repeta cererea daca apare o eroare sau un status de la 500 in sus."""
    status = None
    numar = 0

    for i in range(attempts):
        numar = numar + 1
        try:
            raspuns = requests.get(url, timeout=5)
            status = raspuns.status_code
            if status < 500:
                return {"status": status, "attempts": numar}
        except requests.exceptions.RequestException:
            pass

    if status is None and numar > 0:
        return {"status": None, "error": "Site inaccesibil", "attempts": numar}

    return {"status": status, "attempts": numar}
