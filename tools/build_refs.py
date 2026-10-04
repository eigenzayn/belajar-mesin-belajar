"""Build refs.bib from identifiers only.

Every bibliographic field is taken from Crossref (DOI) or the arXiv API, never typed by hand.
Output: ../book/refs.bib and refs_report.md (what was checked, what failed).
Books are added from books.bib (checked separately, see refs_report.md).
"""
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
IDS = os.path.join(HERE, "refs_ids.txt")
OUT = os.path.join(HERE, os.pardir, "book", "refs.bib")
CACHE = os.path.join(HERE, "refs_cache.json")
REPORT = os.path.join(HERE, "refs_report.md")

cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}


def get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "refcheck/1.0"})
    for k in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            err = e
            time.sleep(15 + 20 * k)  # arXiv answers 429 when asked too fast
    raise err


def tex(s):
    s = re.sub(r"<[^>]+>", "", s)          # strip jats/html tags
    s = re.sub(r"\s+", " ", s).strip()
    rep = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "‐": "-", "‑": "-", "–": "--",
           "—": "---", "’": "'", "‘": "`", "“": "``", "”": "''", " ": " ", " ": " "}
    for a, b in rep.items():
        s = s.replace(a, b)
    uni = {"‐": "-", "‑": "-", "‒": "-", "–": "--", "—": "---", "−": "-",
           "’": "'", "‘": "`", "“": "``", "”": "''", " ": " ", " ": " ", " ": " "}
    for a, b in uni.items():
        s = s.replace(a, b)
    s = s.replace("�ber", "{\\\"U}ber")  # Crossref returns a broken U-umlaut for courant1928
    s = s.replace("$π\\_0$", "$\\pi_0$").replace("π", "$\\pi$")  # arXiv title of black2024
    return s


def crossref(doi):
    if doi in cache:
        return cache[doi]
    j = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")))["message"]
    cache[doi] = j
    return j


def arxiv(aid):
    key = "arxiv:" + aid
    if key in cache:
        return cache[key]
    x = get("http://export.arxiv.org/api/query?id_list=" + aid, accept="application/atom+xml")
    ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
    e = ET.fromstring(x).find("a:entry", ns)
    d = {
        "title": e.find("a:title", ns).text,
        "authors": [a.find("a:name", ns).text for a in e.findall("a:author", ns)],
        "published": e.find("a:published", ns).text,
        "journal_ref": (e.find("ar:journal_ref", ns).text if e.find("ar:journal_ref", ns) is not None else None),
    }
    cache[key] = d
    time.sleep(8)  # arXiv asks for gentle use
    return d


def names_cr(j):
    out = []
    for a in j.get("author", []):
        if "family" in a:
            fam, giv = a["family"], a.get("given", "")
            # Crossref sometimes puts a middle initial or particle into the family field
            # ("D. Jagtap", "Em Karniadakis"); move the leading part back to the given name.
            m = re.match(r"^((?:[A-Z][a-z]?\.?\s)+)([A-Z][\w-]+)$", fam)
            if m and m.group(1).strip().lower() not in {"di", "de", "da", "du", "le", "la"}:
                fam, giv = m.group(2), (giv + " " + m.group(1)).strip()
            out.append(f"{fam}, {giv}".strip(", "))
        elif "name" in a:
            out.append("{" + a["name"] + "}")
    return " and ".join(tex(n) for n in out)


def names_ax(lst):
    out = []
    for n in lst:
        parts = n.split()
        out.append(f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else n)
    return " and ".join(tex(n) for n in out)


def year_cr(j):
    for k in ("published-print", "issued", "published-online", "created"):
        if k in j and j[k].get("date-parts") and j[k]["date-parts"][0][0]:
            return j[k]["date-parts"][0][0]
    return None


entries, report, bad = [], [], []
for line in open(IDS, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, ident, expect = [p.strip() for p in line.split("|")]
    try:
        if ident.startswith("doi:"):
            doi = ident[4:]
            j = crossref(doi)
            title = (j.get("title") or [""])[0]
            f = {"author": names_cr(j), "title": "{" + tex(title) + "}", "year": str(year_cr(j)), "doi": doi}
            typ = j.get("type", "")
            cont = (j.get("container-title") or [""])
            if typ == "proceedings-article":
                kind = "inproceedings"; f["booktitle"] = tex(cont[0]) if cont else ""
            elif typ in ("book", "monograph"):
                kind = "book"; f["publisher"] = tex(j.get("publisher", ""))
            else:
                kind = "article"; f["journal"] = tex(cont[0]) if cont else ""
            for a, b in (("volume", "volume"), ("issue", "number"), ("page", "pages")):
                if j.get(a):
                    f[b] = tex(str(j[a])).replace("-", "--")
        else:
            aid = ident[6:]
            d = arxiv(aid)
            title = d["title"]
            kind = "misc"
            f = {"author": names_ax(d["authors"]), "title": "{" + tex(title) + "}", "year": d["published"][:4],
                 "eprint": aid, "archiveprefix": "arXiv", "howpublished": "arXiv:" + aid}
            if d["journal_ref"]:
                f["note"] = tex(d["journal_ref"])
        ok = expect.lower() in re.sub(r"\s+", " ", title.lower())
        report.append(f"| {key} | {ident} | {'OK' if ok else 'CHECK'} | {tex(title)[:90]} | {f['year']} |")
        if not ok:
            bad.append(key)
        body = ",\n".join(f"  {k} = {{{v}}}" if not v.startswith("{") else f"  {k} = {v}" for k, v in f.items() if v)
        entries.append(f"@{kind}{{{key},\n{body}\n}}\n")
    except Exception as e:
        bad.append(key)
        report.append(f"| {key} | {ident} | FAIL | {e} | |")
    with open(CACHE + ".tmp", "w", encoding="utf-8") as fh:  # atomic: never leave a half-written cache
        json.dump(cache, fh)
    os.replace(CACHE + ".tmp", CACHE)

books = os.path.join(HERE, "books.bib")
extra = open(books, encoding="utf-8").read() if os.path.exists(books) else ""
open(OUT, "w", encoding="utf-8").write("% generated by tools/build_refs.py from Crossref/arXiv\n\n" + "\n".join(entries) + "\n" + extra)
open(REPORT, "w", encoding="utf-8").write(
    "# Reference check\n\n| key | id | status | title (from source) | year |\n|---|---|---|---|---|\n" + "\n".join(report) + "\n")
print(len(entries), "entries;", "problems:", bad)
