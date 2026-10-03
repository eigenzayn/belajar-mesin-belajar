"""Reduce the intensifier 'sangat' in the chapters with varied, natural replacements (one pass, cycling per phrase)."""
import glob, os, re
from itertools import cycle

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = sorted(glob.glob(os.path.join(HERE, os.pardir, "book", "chapters", "*.tex")))

ALT = {
    "besar": ["besar", "besar sekali", "amat besar"],
    "berbeda": ["jauh berbeda", "berbeda"],
    "banyak": ["banyak sekali", "banyak", "amat banyak"],
    "kecil": ["kecil sekali", "kecil", "amat kecil"],
    "dalam": ["dalam", "amat dalam"],
    "cepat": ["cepat sekali", "cepat", "amat cepat"],
    "sulit": ["sulit", "sulit sekali"],
    "sederhana": ["sederhana sekali", "sederhana"],
    "menentukan": ["menentukan", "amat menentukan"],
    "lebar": ["lebar sekali", "lebar"],
    "lambat": ["lambat", "lambat sekali"],
    "jarang": ["jarang sekali", "jarang"],
    "berguna": ["berguna", "amat berguna"],
    "peka": ["peka sekali"], "panjang": ["panjang sekali"], "lama": ["lama sekali"],
    "ketat": ["ketat sekali"], "keras": ["keras sekali"], "cocok": ["cocok sekali"],
}
cycles = {k: cycle(v) for k, v in ALT.items()}
total = 0
for path in FILES:
    s = open(path, encoding="utf-8").read()

    def rep(m):
        global total
        word = m.group(1)
        total += 1
        if word in cycles:
            return next(cycles[word])
        return word  # other adjectives: simply drop the intensifier

    new = re.sub(r"\bsangat ([a-zA-Z\-]+)", rep, s)
    if new != s:
        open(path, "w", encoding="utf-8").write(new)
print("replaced", total)
