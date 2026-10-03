# Belajar Mesin Belajar

Catatan kuliah Master Artificial Intelligence di Linz, ditulis ulang menjadi buku berbahasa Indonesia:
dari neuron sampai difusi, dengan analogi sehari-hari, penurunan rumus, dan contoh hitungan.

- Baca daring: https://eigenzayn.github.io/belajar-mesin-belajar/
- Unduh PDF: [docs/Belajar_Mesin_Belajar.pdf](docs/Belajar_Mesin_Belajar.pdf)

## Isi

Enam bagian, sekitar 35 bab:

1. **Fondasi**: belajar dari data, optimasi, AI klasik, belajar tanpa label
2. **Deep learning dan persepsi**: jaringan saraf, LSTM dan transformer, computer vision, model generatif,
   geometric deep learning, model probabilistik, model difusi dan flow matching, reinforcement learning, XAI
3. **Sinyal, sensor, dan sistem**: estimasi dan filter adaptif, radar, kendali, komputasi pervasif, robot
4. **AI untuk ilmu hayati**: genom, molekul dan obat, protein, citra medis
5. **AI untuk simulasi**: fluida, metode numerik, fisika komputasi, PINN, neural operator, SINDy dan ROM,
   model hibrida, recurrence CFD
6. **AI, manusia, dan masa depan**: sistem rekomendasi, hukum dan masyarakat, perkembangan terbaru

## Struktur repositori

```
book/        sumber LaTeX (main.tex, preamble.tex, chapters/, refs.bib)
tools/       pembangun daftar pustaka dan versi web
docs/        versi web (GitHub Pages) dan PDF
```

## Membangun

```
sh book/build.sh            # PDF (pdflatex + bibtex) ke book/_build/main.pdf
python tools/build_refs.py  # refs.bib dari DOI/arXiv lewat Crossref dan arXiv
python tools/make_html.py   # versi web ke docs/ (butuh pandoc, pdflatex, pdftocairo)
```

Setiap entri di `book/refs.bib` dibangun dari metadata Crossref atau arXiv, bukan diketik tangan.
Buku diperiksa terhadap OpenLibrary atau halaman hak ciptanya. Laporan pemeriksaan ada di
`tools/refs_report.md` dan `tools/refs_report_books.md`.

## Catatan hak cipta

Isi buku ditulis ulang dengan kata-kata sendiri. Slide, naskah, dan soal ujian kuliah tetap milik para
pengajarnya dan tidak disertakan di repositori ini.
