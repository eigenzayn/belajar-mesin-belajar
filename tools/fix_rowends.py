"""Repair table rows whose LaTeX row terminator lost one backslash (a line ending in a single '\')."""
import sys

for path in sys.argv[1:]:
    lines = open(path, encoding="utf-8").read().split("\n")
    out = []
    for ln in lines:
        stripped = ln.rstrip()
        if stripped.endswith("\\") and not stripped.endswith("\\\\"):
            stripped += "\\"
        out.append(stripped if stripped != ln.rstrip() else ln)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print("fixed", path)
