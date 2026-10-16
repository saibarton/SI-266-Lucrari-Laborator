# Munteanu Ion, SI-266 - Laboratorul 5, B1-B4
import re
import zipfile
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

RADACINA = Path(__file__).resolve().parent


def tip_real(cale):
    with open(cale, "rb") as fisier:
        cap = fisier.read(8)
    if cap.startswith(b"%PDF"):
        return "pdf"
    if cap.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if cap.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if cap.startswith(b"PK\x03\x04"):
        return "zip/docx"
    return "necunoscut: " + cap.hex()


def strings(cale):
    date = Path(cale).read_bytes()
    return [text.decode("ascii") for text in re.findall(rb"[ -~]{4,}", date)]


def grade_zecimale(valori, emisfera):
    grade, minute, secunde = valori
    rezultat = float(grade) + float(minute) / 60 + float(secunde) / 3600
    if emisfera in ("S", "W"):
        rezultat = -rezultat
    return rezultat


def citeste_exif(cale):
    with Image.open(cale) as imagine:
        exif = imagine.getexif()
        metadate = {}
        for tag, valoare in exif.items():
            if tag != 34853:
                metadate[TAGS.get(tag, str(tag))] = str(valoare)
        gps = exif.get_ifd(34853)
    coordonate = None
    if all(tag in gps for tag in (1, 2, 3, 4)):
        lat = grade_zecimale(gps[2], gps[1])
        lon = grade_zecimale(gps[4], gps[3])
        coordonate = (lat, lon)
    return metadate, coordonate


def extrage_zip(cale, destinatie):
    date = Path(cale).read_bytes()
    pozitie = date.find(b"PK\x03\x04")
    if pozitie == -1:
        raise ValueError("Nu exista o semnatura ZIP in fisier.")
    destinatie = Path(destinatie)
    destinatie.parent.mkdir(parents=True, exist_ok=True)
    destinatie.write_bytes(date[pozitie:])
    return pozitie


def main():
    probe = RADACINA / "probe"
    rezultate = RADACINA / "rezultate"
    rezultate.mkdir(exist_ok=True)
    print("B1. Tipul real al fisierelor")
    for nume in ("foto.jpg", "ascuns.png"):
        print(nume, "->", tip_real(probe / nume))

    print("\nB2. Text citibil din ascuns.png")
    for text in strings(probe / "ascuns.png"):
        print(text)

    print("\nB3. Metadate EXIF si GPS")
    metadate, coordonate = citeste_exif(probe / "foto.jpg")
    for nume, valoare in sorted(metadate.items()):
        print(nume, "=", valoare)
    if coordonate:
        print("Latitudine: %.6f" % coordonate[0])
        print("Longitudine: %.6f" % coordonate[1])
    else:
        print("Nu exista coordonate GPS.")

    print("\nB4. Arhiva ascunsa")
    arhiva = rezultate / "gasit.zip"
    pozitie = extrage_zip(probe / "ascuns.png", arhiva)
    print("Arhiva extrasa de la octetul", pozitie)
    print("gasit.zip ->", tip_real(arhiva))
    with zipfile.ZipFile(arhiva) as fisier:
        print("Fisiere:", ", ".join(fisier.namelist()))
        secret = fisier.read("secret.txt")
    (rezultate / "secret.txt").write_bytes(secret)
    print("secret.txt:", secret.decode("utf-8").strip())


if __name__ == "__main__":
    main()
