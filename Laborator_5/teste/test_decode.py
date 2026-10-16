import base64
import hashlib
import tempfile
import unittest
from pathlib import Path
from arsenal.forensics.decode import desfa, desfa_straturi, sparge_hash, sparge_xor


class TestDecode(unittest.TestCase):
    def test_base64(self):
        strat, date = desfa("U2FsdXQ=")
        self.assertEqual(strat, "base64")
        self.assertEqual(date, b"Salut")

    def test_hex(self):
        self.assertEqual(desfa("48656c6c6f"), ("hex", b"Hello"))

    def test_url(self):
        self.assertEqual(desfa("%2Fetc%2Fpasswd"), ("url", b"/etc/passwd"))

    def test_straturi_multiple(self):
        clar = b"Mesaj de test!"
        intrare = base64.b64encode(base64.b64encode(clar.hex().encode()))
        rezultat, pasi = desfa_straturi(intrare)
        self.assertEqual(rezultat, clar)
        self.assertEqual([pas["strat"] for pas in pasi], ["base64", "base64", "hex"])

    def test_text_necunoscut(self):
        self.assertEqual(desfa("Text normal!"), ("necunoscut", b"Text normal!"))

    def test_xor(self):
        clar = b"Un mesaj de test. FLAG{test_xor}"
        criptat = bytes(octet ^ 201 for octet in clar)
        scor, cheie, rezultat = sparge_xor(criptat)[0]
        self.assertEqual(cheie, 201)
        self.assertEqual(rezultat, clar.decode())

    def test_hashuri(self):
        with tempfile.TemporaryDirectory() as folder:
            lista = Path(folder) / "wordlist.txt"
            lista.write_text("gresit\ntest123\n", encoding="utf-8")
            for algoritm in ("md5", "sha1", "sha256"):
                tinta = hashlib.new(algoritm, b"test123").hexdigest()
                self.assertEqual(sparge_hash(tinta, lista), (algoritm, "test123"))

    def test_hash_negasit(self):
        with tempfile.TemporaryDirectory() as folder:
            lista = Path(folder) / "wordlist.txt"
            lista.write_text("altceva\n", encoding="utf-8")
            tinta = hashlib.md5(b"test123").hexdigest()
            self.assertEqual(sparge_hash(tinta, lista), ("md5", None))


if __name__ == "__main__":
    unittest.main()
