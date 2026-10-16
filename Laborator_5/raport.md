# Lucrarea de laborator nr. 5

**Disciplina:** Tehnici de programare  
**Tema:** Informații invizibile: forensics și steganografie  
**Student:** Munteanu Ion  
**Grupa:** SI-266  
**Data:** 16.10.2026

## Scopul lucrării

Prelucrarea datelor sub formă de octeți, decodarea unor mesaje și analiza informațiilor ascunse în fișiere. Pentru partea practică am folosit Python și biblioteca Pillow. Fișierele analizate au fost generate cu scriptul `probe/pregateste.py` primit la laborator. Metadatele fotografiei sunt date de test scrise de acest script.

## Lucrarea A. Decoderul universal

### A1. Text și octeți

În `text_octeti.py`, textul `Salut` este transformat în octeți. Primul octet are valoarea `83`, iar reprezentarea hexazecimală este `53616c7574`. Prin `bytes.fromhex()` se obține din nou `b'Salut'`.

### A2-A4. Recunoașterea și desfacerea straturilor

În `arsenal/forensics/decode.py`, funcția `ghici_strat()` verifică întâi codarea URL, apoi hex și Base64. Funcția `desfa()` întoarce tipul și octeții rezultați. Decodarea se repetă de cel mult opt ori.

Pentru `probe/mesaj.txt`, rezultatul este:

```text
Straturi: base64 -> base64 -> hex
Rezultat: FLAG{straturi_de_encoding}
```

Nu am oprit bucla doar pentru că un rezultat intermediar este imprimabil: și un șir hex sau Base64 poate fi text imprimabil. Programul continuă cât timp recunoaște un strat. Recunoașterea după formă rămâne o presupunere: unele texte obișnuite pot avea aceleași caractere ca o codare.

### A5. XOR cu o cheie de un octet

Programul încearcă toate cele 256 de chei și păstrează variantele ASCII imprimabile. Pentru fișierul de laborator au rezultat **17 variante citibile**, deci acest filtru singur nu stabilește sigur cheia. Variantele sunt ordonate după litere, spații și prezența unui mesaj de forma `FLAG{...}`.

Cheia aleasă a fost **128**, adică **0x80**. Mesajul obținut:

```text
Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}
```

Aceeași operație XOR, aplicată cu aceeași cheie încă o dată, reface octeții inițiali. Alegerea prin scor este potrivită pentru probele din laborator, dar nu garantează cheia pentru orice text.

### A6. Hash-uri și dicționar

Cele cinci hash-uri din `probe/hashuri.txt` au câte 32 de caractere hexazecimale și au fost tratate ca MD5. Pentru fiecare cuvânt din `probe/wordlist.txt`, programul calculează hash-ul și îl compară cu ținta.

| Hash MD5 | Parola găsită |
| --- | --- |
| `5f4dcc3b5aa765d61d8327deb882cf99` | `password` |
| `8621ffdbc5698829397d97767ac13db3` | `dragon` |
| `d8578edf8458ce06fbc5bb76a58c5ca4` | `qwerty` |
| `0d107d09f5bbe40cade3de5c71e9e9b7` | `letmein` |
| `d0763edaa9d9bd2a9516280e9044d885` | `monkey` |

Hash-ul nu este decriptat. Parola este găsită prin încercarea cuvintelor. Funcția acceptă și SHA1, respectiv SHA256, presupuse după lungimile de 40 și 64 de caractere. Lungimea oferă un indiciu, nu o identificare sigură în toate cazurile.

### A7. Argumente, fișa JSON și teste

Decoderul primește un șir sau, cu `--fisier`, o cale. Opțiunile `--xor` și `--hash` permit alegerea explicită a operației. `--wordlist` schimbă dicționarul, iar `--fisa` stabilește fișierul JSON de ieșire.

`arsenal/forensics/fisa.json` conține mesajul decodat și straturile sale. Rezultatele XOR și hash sunt salvate separat în `rezultate/xor.json` și `rezultate/hashuri.json`.

## Lucrarea B. Analiza fișierelor

### B1. Tipul real

Scriptul `forensics.py` citește semnăturile în mod binar.

| Fișier | Semnătura de început | Tip identificat |
| --- | --- | --- |
| `probe/foto.jpg` | `FF D8 FF` | JPEG |
| `probe/ascuns.png` | `89 50 4E 47 0D 0A 1A 0A` | PNG |
| `rezultate/gasit.zip` | `50 4B 03 04` | ZIP; semnătură comună cu DOCX |

### B2. Text citibil din fișier

Prin expresia `rb"[ -~]{4,}"` sunt căutate secvențe de cel puțin patru caractere imprimabile. În `ascuns.png` apar numele `secret.txt` și mesajul `FLAG{ascuns_prin_carving}`. Acestea indică date suplimentare în fișier.

### B3. Metadate EXIF și GPS

Din `probe/foto.jpg` au fost citite:

| Câmp | Valoare |
| --- | --- |
| Make | Apple |
| Model | iPhone 13 |
| DateTime | 2026:09:14 10:30:00 |
| Latitudine | 47.016667 N |
| Longitudine | 28.857500 E |

Conversia coordonatelor:

```text
Latitudine = 47 + 1/60 + 0/3600 = 47.016666...
Longitudine = 28 + 51/60 + 27/3600 = 28.8575
```

Coordonatele de test sunt pentru Chișinău. Pentru emisferele sudică și vestică, valoarea calculată primește semnul minus.

### B4. Extragerea arhivei ascunse

Semnătura ZIP `PK\x03\x04` a fost găsită în `probe/ascuns.png` la **poziția 782**, numărând de la zero. Octeții începând din acel loc au fost salvați în `rezultate/gasit.zip`.

Arhiva conține `secret.txt`, cu textul:

```text
FLAG{ascuns_prin_carving}
```

Poziția de mai sus este cea obținută pentru proba inclusă. La regenerare, versiunea bibliotecii de imagini poate schimba dimensiunea PNG și poziția arhivei. Scriptul caută semnătura, fără o poziție fixată în cod.

### B5-B6. Ascunderea și citirea mesajului LSB

În `stego.py`, mesajul este transformat în UTF-8 și apoi în biți. La sfârșit se adaugă un octet zero, pentru a ști unde se termină textul. Biții sunt scriși în ultimul bit al canalelor roșu, verde și albastru, în această ordine.

Imaginea este salvată în `stego.png`. La citire, ultimii biți sunt grupați câte opt până la octetul zero. Mesajul recuperat a fost:

```text
FLAG{ascuns_in_pixeli}
```

Fiecare canal modificat diferă cu cel mult o unitate. PNG păstrează valorile pixelilor; salvarea în JPEG poate distruge mesajul ascuns prin recompresie.

## Rulare și verificare

Comenzile se execută din folderul `Laborator_5`:

```text
python -m pip install -r requirements.txt
python probe/pregateste.py
python text_octeti.py
python arsenal/forensics/decode.py probe/mesaj.txt --fisier
python arsenal/forensics/decode.py probe/xor.bin --fisier --xor --fisa rezultate/xor.json
python arsenal/forensics/decode.py probe/hashuri.txt --fisier --hash --fisa rezultate/hashuri.json
python forensics.py
python stego.py ascunde probe/foto.jpg
python stego.py dezvaluie stego.png
python -m unittest discover -s teste -v
```

Verificarea a fost efectuată cu **Python 3.12.14** și **Pillow 12.3.0**. Au trecut **13 teste**, pentru decodare, XOR, hash-uri, semnături, GPS, carving și LSB. Testele folosesc `unittest`, inclus în Python. Output-ul comenzilor se află în `rezultate/output.txt`, iar rezultatul testelor în `rezultate/teste.txt`.

Fișierele `challenge.bin` și `challenge_hint.txt` sunt generate de scriptul primit și țin de exercițiul opțional. Rezultatele prezentate aici acoperă A1-A7 și B1-B6.

## Concluzie

Am folosit octeți și operații pe biți pentru a decoda mesaje și a găsi informații ascunse în fișiere. Am observat că o codare nu protejează un mesaj, o cheie XOR de un octet poate fi încercată prin toate variantele, iar parolele din dicționar sunt ușor de găsit. Metadatele pot dezvălui locul unei fotografii, de aceea trebuie verificate înainte de publicare. Pentru protecția parolelor sunt necesare parole lungi și unice și metode de stocare dedicate acestora. Toate probele analizate provin din generatorul laboratorului.

## Materiale folosite

1. Fișa „Laboratorul 5. Informații invizibile: forensics și steganografie”.
2. Cursul „Sesiunea 6. Informații invizibile: forensics și steganografie”.
3. Scriptul de pregătire `probe_pregateste.py`, furnizat pentru laborator și păstrat ca `probe/pregateste.py`.
