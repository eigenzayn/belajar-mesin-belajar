#!/bin/sh
# Build the book: pdflatex, bibtex, pdflatex x2 into _build/, then copy the PDF next to the sources.
cd "$(dirname "$0")"
mkdir -p _build
run() { pdflatex -interaction=nonstopmode -halt-on-error -output-directory=_build main.tex >> _build/build.log 2>&1; }
: > _build/build.log
run || { grep -n -A6 "^!" _build/main.log | head -30; exit 1; }
BIBINPUTS=".;" bibtex _build/main >> _build/build.log 2>&1
run
python ../tools/fix_idx.py _build/main.idx
makeindex -q _build/main.idx >> _build/build.log 2>&1
run
grep -E "Warning: (Citation|Reference).*undefined" _build/main.log | sort -u | head -20
echo "overfull: $(grep -c 'Overfull' _build/main.log)"
cp _build/main.pdf Belajar_Mesin_Belajar.pdf 2>/dev/null || echo "note: Belajar_Mesin_Belajar.pdf is open elsewhere, fresh copy is in _build/main.pdf"
python -c "import fitz;print('pages',len(fitz.open('_build/main.pdf')))"
