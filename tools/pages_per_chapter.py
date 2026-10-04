"""Print the page count of every chapter from book/_build/main.toc (run after a PDF build)."""
import os, re
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, os.pardir, "book", "_build")
toc = open(os.path.join(B, "main.toc"), encoding="utf-8", errors="replace").read()
rows = []
for m in re.finditer(r"\\contentsline \{chapter\}\{(?:\\numberline \{([^}]*)\})?([^}]*)\}\{(\d+)\}", toc):
    rows.append((int(m.group(3)), m.group(1) or "", m.group(2)))
total = len(fitz.open(os.path.join(B, "main.pdf")))
for i, (p, num, title) in enumerate(rows):
    end = rows[i + 1][0] if i + 1 < len(rows) else total
    print(f"{num:>3} {end - p:>3} hlm  {title[:60]}")
