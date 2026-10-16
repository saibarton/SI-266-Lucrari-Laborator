# Munteanu Ion, SI-266 - Laboratorul 5, B5-B6
import argparse
from pathlib import Path
from PIL import Image

RADACINA = Path(__file__).resolve().parent


def ascunde(cale, mesaj, destinatie):
    if "\0" in mesaj:
        raise ValueError("Mesajul nu poate contine octetul de sfarsit 0.")
    with Image.open(cale) as original:
        imagine = original.convert("RGB")
    date = mesaj.encode("utf-8") + b"\x00"
    biti = "".join(format(octet, "08b") for octet in date)
    if len(biti) > imagine.width * imagine.height * 3:
        raise ValueError("Mesajul nu incape in imagine.")
    pixeli = list(imagine.getdata())
    pozitie = 0
    for i in range(len(pixeli)):
        canale = list(pixeli[i])
        for j in range(3):
            if pozitie < len(biti):
                canale[j] = (canale[j] & ~1) | int(biti[pozitie])
                pozitie += 1
        pixeli[i] = tuple(canale)
        if pozitie == len(biti):
            break
    imagine.putdata(pixeli)
    imagine.save(destinatie, format="PNG")


def dezvaluie(cale):
    with Image.open(cale) as sursa:
        imagine = sursa.convert("RGB")
    date = bytearray()
    octet = 0
    numar_biti = 0
    for pixel in imagine.getdata():
        for canal in pixel:
            octet = (octet << 1) | (canal & 1)
            numar_biti += 1
            if numar_biti == 8:
                if octet == 0:
                    return date.decode("utf-8")
                date.append(octet)
                octet = 0
                numar_biti = 0
    raise ValueError("Nu a fost gasit octetul de sfarsit al mesajului.")


def main():
    p = argparse.ArgumentParser(description="Ascunde sau citeste un mesaj LSB")
    p.add_argument("operatie", choices=["ascunde", "dezvaluie"])
    p.add_argument("imagine")
    p.add_argument("--mesaj", default="FLAG{ascuns_in_pixeli}")
    p.add_argument("--iesire", default=str(RADACINA / "stego.png"))
    a = p.parse_args()
    try:
        if a.operatie == "ascunde":
            ascunde(a.imagine, a.mesaj, a.iesire)
            print("Imagine salvata:", Path(a.iesire).name)
            print("Mesaj ascuns:", a.mesaj)
        else:
            print("Mesaj dezvaluit:", dezvaluie(a.imagine))
    except (OSError, ValueError) as eroare:
        p.exit(1, "Eroare: " + str(eroare) + "\n")


if __name__ == "__main__":
    main()
