import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image
from forensics import tip_real, grade_zecimale, extrage_zip
from stego import ascunde, dezvaluie


class TestFisiere(unittest.TestCase):
    def setUp(self):
        self.temporar = tempfile.TemporaryDirectory()
        self.folder = Path(self.temporar.name)

    def tearDown(self):
        self.temporar.cleanup()

    def test_magic_bytes(self):
        cale = self.folder / "poza.txt"
        Image.new("RGB", (4, 4)).save(cale, format="PNG")
        self.assertEqual(tip_real(cale), "png")

    def test_gps(self):
        self.assertAlmostEqual(grade_zecimale((47, 1, 0), "N"), 47.0166667, places=6)
        self.assertAlmostEqual(grade_zecimale((28, 51, 27), "E"), 28.8575)
        self.assertAlmostEqual(grade_zecimale((28, 51, 27), "W"), -28.8575)

    def test_carving(self):
        arhiva = self.folder / "date.zip"
        with zipfile.ZipFile(arhiva, "w") as fisier:
            fisier.writestr("test.txt", "mesaj")
        intrare = self.folder / "ascuns.bin"
        intrare.write_bytes(b"inceput" + arhiva.read_bytes())
        rezultat = self.folder / "gasit.zip"
        self.assertEqual(extrage_zip(intrare, rezultat), 7)
        with zipfile.ZipFile(rezultat) as fisier:
            self.assertEqual(fisier.read("test.txt"), b"mesaj")

    def test_lsb(self):
        gazda = self.folder / "gazda.png"
        rezultat = self.folder / "stego.png"
        Image.new("RGB", (40, 40), (70, 110, 160)).save(gazda)
        mesaj = "Salut, Ionuț!"
        ascunde(gazda, mesaj, rezultat)
        self.assertEqual(dezvaluie(rezultat), mesaj)
        with Image.open(gazda) as original, Image.open(rezultat) as modificat:
            for a, b in zip(original.getdata(), modificat.getdata()):
                self.assertTrue(all(abs(x - y) <= 1 for x, y in zip(a, b)))

    def test_lsb_mesaj_prea_lung(self):
        gazda = self.folder / "mic.png"
        Image.new("RGB", (1, 1)).save(gazda)
        with self.assertRaises(ValueError):
            ascunde(gazda, "Salut", self.folder / "stego.png")


if __name__ == "__main__":
    unittest.main()
