# Munteanu Ion, SI-266 - Laboratorul 5, lucrarea A
import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote_to_bytes

RADACINA = Path(__file__).resolve().parents[2]


def ghici_strat(s):
    s = s.strip()
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"
    if s and len(s) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", s):
        return "hex"
    if s and len(s) % 4 == 0 and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s):
        return "base64"
    return "necunoscut"


def desfa(s):
    strat = ghici_strat(s)
    s = s.strip()
    try:
        if strat == "url":
            return strat, unquote_to_bytes(s)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
    except (ValueError, binascii.Error):
        return "necunoscut", s.encode("utf-8")
    return strat, s.encode("utf-8")


def citibil(date):
    return bool(date) and all(32 <= octet < 127 for octet in date)


def desfa_straturi(date):
    pasi = []
    for _ in range(8):
        try:
            text = date.decode("utf-8")
        except UnicodeDecodeError:
            break
        strat, rezultat = desfa(text)
        if strat == "necunoscut" or rezultat == date:
            break
        pasi.append({"strat": strat, "rezultat_hex": rezultat.hex()})
        date = rezultat
    return date, pasi


def sparge_xor(date):
    variante = []
    for cheie in range(256):
        clar = bytes(octet ^ cheie for octet in date)
        if citibil(clar):
            text = clar.decode("ascii")
            # Mai multe chei pot da ASCII. Prefer literele si spatiile.
            scor = sum(c.isalpha() or c == " " for c in text)
            scor += text.count(" ") * 2
            if re.search(r"FLAG\{[^}]+\}", text):
                scor += 100
            variante.append((scor, cheie, text))
    variante.sort(reverse=True)
    return variante


def tip_hash(tinta):
    if not re.fullmatch(r"[0-9a-fA-F]+", tinta):
        return None
    return {32: "md5", 40: "sha1", 64: "sha256"}.get(len(tinta))


def sparge_hash(tinta, wordlist):
    algoritm = tip_hash(tinta)
    if algoritm is None:
        raise ValueError("Hash nerecunoscut: sunt acceptate MD5, SHA1 si SHA256.")
    with open(wordlist, encoding="latin1") as fisier:
        for linie in fisier:
            cuvant = linie.strip()
            calculat = hashlib.new(algoritm, cuvant.encode("utf-8")).hexdigest()
            if calculat == tinta.lower():
                return algoritm, cuvant
    return algoritm, None


def main():
    p = argparse.ArgumentParser(description="Decoder pentru probele laboratorului 5")
    p.add_argument("intrare", help="sir sau cale catre fisier")
    p.add_argument("--fisier", action="store_true")
    mod = p.add_mutually_exclusive_group()
    mod.add_argument("--xor", action="store_true", help="incearca toate cheile XOR")
    mod.add_argument("--hash", action="store_true", help="cauta hash-ul in dictionar")
    p.add_argument("--wordlist", default=str(RADACINA / "probe/wordlist.txt"))
    p.add_argument("--fisa", default=str(Path(__file__).with_name("fisa.json")))
    a = p.parse_args()

    try:
        if a.fisier:
            date = Path(a.intrare).read_bytes()
        else:
            date = a.intrare.encode("utf-8")
        text = date.decode("utf-8", errors="replace").strip()
        linii = [linie.strip() for linie in text.splitlines() if linie.strip()]
        sunt_hashuri = bool(linii) and all(tip_hash(linie) for linie in linii)

        if a.hash or (sunt_hashuri and not a.xor):
            rezultate = []
            for tinta in linii:
                algoritm, parola = sparge_hash(tinta, a.wordlist)
                rezultate.append({"hash": tinta, "algoritm": algoritm, "parola": parola})
                print(algoritm, tinta, "->", parola if parola is not None else "negasit")
            fisa = {"strat": "hash", "rezultat": rezultate}
        else:
            pasi = []
            if not a.xor:
                date, pasi = desfa_straturi(date)
            fisa = {"strat": " -> ".join(pas["strat"] for pas in pasi), "pasi": pasi}
            try:
                rezultat = date.decode("utf-8")
                este_text = all(c.isprintable() or c in "\r\n\t" for c in rezultat)
            except UnicodeDecodeError:
                este_text = False
            if a.xor or not este_text:
                variante = sparge_xor(date)
                if not variante:
                    raise ValueError("Nu a fost gasit un rezultat XOR citibil.")
                scor, cheie, rezultat = variante[0]
                fisa["strat"] = (fisa["strat"] + " -> xor").lstrip(" ->")
                fisa["cheie"] = cheie
                fisa["variante_citibile"] = len(variante)
                print("Cheie XOR:", cheie, "=" , hex(cheie))
                print("Variante ASCII citibile:", len(variante))
            fisa["strat"] = fisa["strat"] or "necunoscut"
            fisa["rezultat"] = rezultat
            print("Straturi:", fisa["strat"])
            print("Rezultat:", rezultat)

        destinatie = Path(a.fisa)
        destinatie.parent.mkdir(parents=True, exist_ok=True)
        destinatie.write_text(json.dumps(fisa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Fisa salvata:", destinatie.name)
    except (OSError, ValueError) as eroare:
        p.exit(1, "Eroare: " + str(eroare) + "\n")


if __name__ == "__main__":
    main()
