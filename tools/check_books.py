"""Check every @book in books.bib against OpenLibrary (title + first author surname + year in edition years)."""
import json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "books.bib"), encoding="utf-8").read()
rows = []
for m in re.finditer(r"@book\{(\w+),(.*?)\n\}", src, re.S):
    key, body = m.group(1), m.group(2)
    f = dict(re.findall(r"(\w+) = \{(.*?)\}\s*,?\n", body + "\n"))
    title = f["title"].split(":")[0]
    surname = re.sub(r"[{}\\'`]", "", f["author"].split(",")[0])
    q = urllib.parse.urlencode({"title": title, "author": surname, "fields": "title,author_name,publish_year,publisher", "limit": 5})
    try:
        j = json.loads(urllib.request.urlopen("https://openlibrary.org/search.json?" + q, timeout=40).read())
        years = sorted({y for d in j.get("docs", []) for y in d.get("publish_year", [])})
        found = j.get("numFound", 0) > 0
        yr_ok = int(f["year"]) in years
        status = "OK" if found and yr_ok else ("TITLE OK, YEAR?" if found else "NOT FOUND")
        rows.append(f"| {key} | {f['title'][:60]} | {f['year']} | {status} | {years[-8:]} |")
    except Exception as e:
        rows.append(f"| {key} | {f['title'][:60]} | {f['year']} | ERROR {e} | |")
    time.sleep(1)
open(os.path.join(HERE, "refs_report_books.md"), "w", encoding="utf-8").write(
    "# Book check (OpenLibrary)\n\n| key | title | year | status | edition years seen |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
print("\n".join(rows))
