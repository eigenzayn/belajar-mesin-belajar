"""Build the web edition of the book (one HTML page per chapter) into ../docs.

Steps
1. Read label numbers from book/_build/main.aux (so the PDF must be built first).
2. For every chapter: resolve \\cref/\\ref/\\eqref, turn every tikzpicture into an SVG
   (standalone pdflatex + pdftocairo), simplify a few LaTeX constructs pandoc does not know.
3. Run pandoc (LaTeX -> HTML5, MathJax, citeproc with book/refs.bib) into a shared template.
"""
import glob, os, re, shutil, subprocess, sys, hashlib, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
BOOK = os.path.join(ROOT, "book")
OUT = os.path.join(ROOT, "docs")
FIG = os.path.join(OUT, "fig")
TMP = os.path.join(ROOT, "_htmlbuild")
B = "\\"

# ------------------------------------------------------------------ labels from aux
def read_labels():
    aux = open(os.path.join(BOOK, "_build", "main.aux"), encoding="utf-8", errors="replace").read()
    labels, kinds = {}, {}
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", aux):
        key, num = m.group(1), m.group(2)
        if key.endswith("@cref"):
            k = re.match(r"\[(\w+)\]", num)
            if k:
                kinds[key[:-5]] = k.group(1)
        else:
            labels[key] = num
    return labels, kinds

LABELS, KINDS = read_labels()
NAMES = {"chapter": "Bab", "section": "Subbab", "subsection": "Subbab", "equation": "Persamaan",
         "figure": "Gambar", "table": "Tabel", "part": "Bagian", "appendix": "Lampiran"}

def ref_text(key, capital=False):
    num = LABELS.get(key, "?")
    kind = KINDS.get(key, "chapter" if key.startswith("ch:") else "")
    name = NAMES.get(kind, "")
    if kind == "equation":
        num = f"({num})"
    if key.startswith("lamp:"):
        name = "Lampiran"
    link = chapter_link(key)
    txt = f"{name} {num}".strip()
    return f"\\href{{{link}}}{{{txt}}}" if link else txt

CHAPTER_OF = {}  # label -> chapter html file, filled per chapter

def chapter_link(key):
    if key.startswith("ch:") and key in CHAPTER_OF:
        return CHAPTER_OF[key]
    return ""

def group(s, i):
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == B:
            j += 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced " + s[i:i + 50])

def replace_cmd(s, name, fn):
    out, i = [], 0
    pat = re.compile(re.escape(B + name) + r"(?![A-Za-z])\s*")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); return "".join(out)
        if m.end() >= len(s) or s[m.end()] != "{":
            out.append(s[i:m.end()]); i = m.end(); continue
        arg, j = group(s, m.end())
        out.append(s[i:m.start()]); out.append(fn(arg)); i = j

def crefs(arg):
    keys = [k.strip() for k in arg.split(",")]
    parts = [ref_text(k) for k in keys]
    if len(parts) == 1:
        return parts[0]
    # "Bab 3, Bab 4 dan Bab 5" -> keep names, join naturally
    return ", ".join(parts[:-1]) + " dan " + parts[-1]

# ------------------------------------------------------------------ tikz -> svg
STANDALONE = r"""\documentclass[tikz,border=4pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{amsmath,mathtools,bm}
\usepackage{newpxtext,newpxmath}
\usepackage[scaled=0.93]{sourcesans}
\usepackage{pgfplots}
\input{tikzstyles}
\begin{document}
%s
\end{document}
"""

def tikz_to_svg(code):
    h = hashlib.sha1(code.encode("utf-8")).hexdigest()[:12]
    svg = os.path.join(FIG, h + ".svg")
    if not os.path.exists(svg):
        work = os.path.join(TMP, "tikz")
        os.makedirs(work, exist_ok=True)
        shutil.copy(os.path.join(BOOK, "tikzstyles.tex"), work)
        tex = os.path.join(work, h + ".tex")
        open(tex, "w", encoding="utf-8").write(STANDALONE % code)
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", h + ".tex"],
                           cwd=work, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            print("  tikz failed", h, r.stdout[-600:]); return ""
        subprocess.run(["pdftocairo", "-svg", h + ".pdf", svg], cwd=work, check=True)
    return f"fig/{h}.svg"

def figures(s):
    def rep(m):
        code = m.group(0)
        # resolve refs inside the picture before compiling
        code = replace_cmd(code, "ref", lambda a: LABELS.get(a.strip(), "?"))
        src = tikz_to_svg(code)
        return f"\\includegraphics{{{src}}}" if src else ""
    return re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", rep, s, flags=re.S)

# ------------------------------------------------------------------ simplify LaTeX for pandoc
MACROS = r"""
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\N}{\mathcal{N}}
\newcommand{\Loss}{\mathcal{L}}
\newcommand{\dd}{\,\mathrm{d}}
\newcommand{\vx}{\boldsymbol{x}}
\newcommand{\vy}{\boldsymbol{y}}
\newcommand{\vz}{\boldsymbol{z}}
\newcommand{\vw}{\boldsymbol{w}}
\newcommand{\vu}{\boldsymbol{u}}
\newcommand{\vh}{\boldsymbol{h}}
\newcommand{\vtheta}{\boldsymbol{\theta}}
\newcommand{\mW}{\boldsymbol{W}}
\newcommand{\mA}{\boldsymbol{A}}
\newcommand{\mX}{\boldsymbol{X}}
\newcommand{\KL}{\mathrm{KL}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
\newcommand{\argmax}{\operatorname*{arg\,max}}
"""

def simplify(s):
    s = re.sub(r"(?m)^%.*$", "", s)
    s = re.sub(r"\\bm(?![A-Za-z])", lambda m: B + "boldsymbol", s)
    s = replace_cmd(s, "istilah", lambda a: B + "emph{" + a + "}")
    s = replace_cmd(s, "sumberbab", lambda a: "\n\n" + B + "paragraph{Catatan sumber.} " + a + "\n\n")
    for c in ("Cref", "cref"):
        s = replace_cmd(s, c, crefs)
    s = replace_cmd(s, "eqref", lambda a: ref_text(a.strip()))
    s = replace_cmd(s, "ref", lambda a: LABELS.get(a.strip(), "?"))
    s = re.sub(r"\\begin\{description\}\[[^\]]*\]", r"\\begin{description}", s)
    s = re.sub(r"\\begin\{itemize\}\[[^\]]*\]", r"\\begin{itemize}", s)

    def tabx(m):
        spec = re.sub(r"@\{\}", "", m.group(1))
        n = len(re.findall(r"p\{[^}]*\}|[lcrX]", spec))
        return B + "begin{tabular}{" + "l" * n + "}"
    s = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}", tabx, s)
    s = s.replace(B + "end{tabularx}", B + "end{tabular}")
    s = re.sub(r"\\(small|centering|footnotesize|medskip|bigskip|smallskip|hfill|noindent)\b", "", s)
    return s

# ------------------------------------------------------------------ book structure
def structure():
    main = open(os.path.join(BOOK, "main.tex"), encoding="utf-8").read()
    items = []
    for m in re.finditer(r"\\part\{([^}]*)\}|\\bab\{([^}]*)\}", main):
        if m.group(1):
            items.append(("part", m.group(1)))
        elif os.path.exists(os.path.join(BOOK, "chapters", m.group(2) + ".tex")):
            items.append(("chapter", m.group(2)))
    return items

def chapter_meta(name):
    src = open(os.path.join(BOOK, "chapters", name + ".tex"), encoding="utf-8").read()
    title = re.search(r"\\chapter\*?\{([^}]*)\}", src).group(1)
    label = re.search(r"\\label\{([^}]*)\}", src)
    label = label.group(1) if label else ""
    num = LABELS.get(label, "")
    return src, title, label, num

def main():
    os.makedirs(FIG, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    items = structure()
    chapters = [n for k, n in items if k == "chapter"]
    for n in chapters:
        _, _, label, _ = chapter_meta(n)
        if label:
            CHAPTER_OF[label] = n + ".html"
    template = os.path.join(HERE, "web_template.html")
    toc = []
    order = ["prakata"] + chapters
    titles = {}
    for n in order:
        src, title, label, num = chapter_meta(n)
        titles[n] = (title, num)
    for idx, n in enumerate(order):
        src, title, label, num = chapter_meta(n)
        body = simplify(figures(src))
        body = re.sub(r"\\chapter\*?\{[^}]*\}", "", body, count=1)
        body = re.sub(r"\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}", "", body)
        texfile = os.path.join(TMP, n + ".tex")
        open(texfile, "w", encoding="utf-8").write(MACROS + body)
        prev_n = order[idx - 1] if idx > 0 else None
        next_n = order[idx + 1] if idx + 1 < len(order) else None
        heading = (f"Bab {num}" if num and not n.startswith("lamp") else ("Lampiran " + num if num else ""))
        args = ["pandoc", texfile, "-f", "latex", "-t", "html5", "--mathjax", "--citeproc",
                "--bibliography", os.path.join(BOOK, "refs.bib"),
                "--metadata", "lang=id", "--metadata", f"title={title}",
                "--metadata", "reference-section-title=Pustaka bab ini",
                "--variable", f"chapnum={heading}",
                "--template", template, "-o", os.path.join(OUT, n + ".html")]
        if prev_n:
            args += ["--variable", f"prev={prev_n}.html", "--variable", f"prevtitle={titles[prev_n][0]}"]
        if next_n:
            args += ["--variable", f"next={next_n}.html", "--variable", f"nexttitle={titles[next_n][0]}"]
        r = subprocess.run(args, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            print("pandoc failed", n, r.stderr[-800:]); sys.exit(1)
        warn = [l for l in r.stderr.splitlines() if "WARNING" in l or "Could not" in l]
        print(f"{n}: ok" + (f"  ({len(warn)} warnings)" if warn else ""))
    # index
    parts_html = []
    for k, v in items:
        if k == "part":
            parts_html.append(f"<h3>{html.escape(v)}</h3><ol class='toc'>")
        else:
            t, num = titles[v]
            pre = f"<span class='num'>{num}</span> " if num else ""
            parts_html.append(f"<li><a href='{v}.html'>{pre}{html.escape(t)}</a></li>")
    joined = ["<ol class='toc'>", "<li><a href='prakata.html'>Prakata</a></li>"]
    open_ol = True
    for h in parts_html:
        if h.startswith("<h3>"):
            if open_ol:
                joined.append("</ol>")
            joined.append(h); open_ol = True
        else:
            joined.append(h)
    if open_ol:
        joined.append("</ol>")
    idx_html = open(os.path.join(HERE, "web_index.html"), encoding="utf-8").read().replace("{{TOC}}", "\n".join(joined))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(idx_html)
    shutil.copy(os.path.join(HERE, "web_style.css"), os.path.join(OUT, "style.css"))
    pdf = os.path.join(BOOK, "_build", "main.pdf")
    shutil.copy(pdf, os.path.join(OUT, "Belajar_Mesin_Belajar.pdf"))
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print("done ->", OUT)

if __name__ == "__main__":
    main()
