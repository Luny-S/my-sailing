# TODO

- [x] Make base names all english
- [x] Replicate *karta rejsu* as a fillable form (passage-card)
- [x] Replicate *opinia z rejsu* / crew member's certificate of passage (crew-opinion)
- [x] Per-crew-member generation: one crew-opinion copy per crew member (merged PDF)
- [x] Bilingual fields (cert / rank / captain_cert / remarks) — `{pl, en}` or a plain string

## Open

- [ ] **Field text overflow** (major): long values (e.g. a long "Yachtmaster
      Offshore No. …") overflow the fixed-width field. Auto-fit on fill: shrink
      the drawn font size to the field width (and/or wrap), so nothing clips.
- [ ] **crew-opinion alignment**: tidy the OPINIA KAPITANA checkbox table
      (trailing column / option spacing) and overall vertical spacing.
- [x] **Tech decision**: print-only, pre-filled PDFs (no interactive fill
      needed) → move to **HTML + CSS + WeasyPrint**. Feasibility confirmed:
      WeasyPrint renders A4 with full Polish diacritics + bordered tables in
      this container (system libs: libpango/cairo/gdk-pixbuf, fonts-dejavu).
- [ ] **Rewrite the forms in HTML/CSS + WeasyPrint** (print-only, pre-filled):
      - Jinja2 templates bind the existing pydantic models directly (no flat
        AcroForm field-name mapping); render PL + EN pages, loop crew for
        crew-opinion (one form per member).
      - CSS solves the LaTeX pain points: field auto-fit/wrapping (no overflow),
        easier alignment, `@page { size: A4 }` for print.
      - Add weasyprint + jinja2 deps; a render module + CLI (replace/augment
        `fill-doc`); reuse documents/shared/assets/pzz-logo.png.
      - Port passage-card first (spike), then crew-opinion; retire the LaTeX
        forms once parity is reached.
- [ ] Make the other skeleton docs (safety-briefing, shopping-list, packing-list,
      yacht-log, yacht-check-in) into real fillable forms + models, if wanted.
