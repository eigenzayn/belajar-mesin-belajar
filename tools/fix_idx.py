"""Normalise index entries written by \\istilah before makeindex runs.

Terms that start a sentence are capitalised in the text ("Average precision"), which would give a second
index entry next to "average precision". This script lower-cases the first letter of such entries (keeping
proper names and acronyms), collapses line breaks inside terms, and adds a lower-case sort key, so that
makeindex merges them into one entry.
"""
import re
import sys

PROPER = ("Bayes", "Bayesian", "Markov", "Kalman", "Gibbs", "Fisher", "Hessian", "Laplace", "Monte", "Nash",
          "Pareto", "Reynolds", "Riemannian", "Weisfeiler", "Hough", "Bremsstrahlung", "Airborne")

ENTRY = re.compile(r"^\\indexentry\{(.*)\}\{(.*)\}\s*$")


def display(term: str) -> str:
    term = re.sub(r"\s+", " ", term).strip()
    first = term.split(" ")[0].split("-")[0]
    if first in PROPER:
        return term
    if len(term) > 1 and term[0].isupper() and term[1].islower():
        return term[0].lower() + term[1:]
    return term


def sort_key(term: str) -> str:
    key = re.sub(r"\$[^$]*\$", "", term)          # drop inline math such as $k$
    key = re.sub(r"[{}\\]", "", key)
    return key.strip().lower() or term.lower()


def main(path: str) -> None:
    out = []
    for line in open(path, encoding="utf-8"):
        m = ENTRY.match(line)
        if not m:
            out.append(line)
            continue
        term, bar, fmt = m.group(1).partition("|")   # hyperref appends "|hyperpage"
        shown = display(term)
        out.append("\\indexentry{%s@%s%s%s}{%s}\n" % (sort_key(shown), shown, bar, fmt, m.group(2)))
    open(path, "w", encoding="utf-8").write("".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
