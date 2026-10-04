# Belajar Mesin Belajar

Catatan kuliah Master Artificial Intelligence di Linz, ditulis ulang dan diperluas menjadi buku berbahasa Indonesia:
dari data dan neuron sampai sinyal, molekul, dan fluida, dengan analogi sehari-hari, penurunan rumus, dan contoh hitungan.

- Baca daring: https://eigenzayn.github.io/belajar-mesin-belajar/
- Unduh PDF: [docs/Belajar_Mesin_Belajar.pdf](docs/Belajar_Mesin_Belajar.pdf)

## Isi

Enam bagian berisi 38 bab ditambah Peta Perjalanan, tiga lampiran, dan indeks:

1. **Fondasi**: belajar dari data, statistik dan Bayes untuk memilih model, teori belajar statistik, optimasi,
   AI klasik, belajar tanpa label
2. **Deep learning dan persepsi**: jaringan saraf dan praktiknya, LSTM sampai xLSTM, bahasa (NLP), computer vision,
   model generatif, geometric deep learning, model probabilistik, Gaussian process dan model difusi,
   reinforcement learning, XAI
3. **Sinyal, sensor, dan sistem**: estimasi dan filter adaptif, radar, kendali, komputasi pervasif, robot
4. **AI untuk ilmu hayati**: genom, molekul dan obat, protein, citra medis
5. **AI untuk simulasi**: fluida, metode numerik, fisika komputasi, PINN, neural operator, SINDy dan ROM,
   model hibrida, recurrence CFD
6. **AI, manusia, dan masa depan**: sistem rekomendasi, hukum dan masyarakat, keselamatan AI, informasi kuantum,
   perkembangan terbaru

Lampiran: glosarium, bekal matematika, dan panduan meneliti, menerbitkan, dan mematenkan.
Hampir setiap bab ditutup dengan bagian *Perkembangan riset* yang merangkum makalah beberapa tahun terakhir.

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

Isi buku ditulis ulang dengan kata-kata sendiri dari kuliah yang diikuti, lalu diperluas dengan bacaan di luar
kuliah (bagian perkembangan riset, beberapa bab dari literatur, dan lampiran). Slide, naskah, dan soal ujian kuliah
tetap milik para pengajarnya dan tidak disertakan di repositori ini.
