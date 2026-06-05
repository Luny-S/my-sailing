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
- [x] **Rewrite the forms in HTML/CSS + WeasyPrint** (print-only, pre-filled):
      `render-doc <doc> data.json -o out.pdf`. Jinja2 templates
      (src/my_sailing/templates/) bound to the pydantic models; PL+EN pages,
      crew-opinion fans out to one form per member; checkboxes for the opinion
      assessment; CSS field-wrapping fixes the overflow; `@page A4`.
      passage-card (2pp) and crew-opinion (2pp/member) both at parity.

## Follow-ups

- [ ] Retire the LaTeX path once happy with HTML (remove documents/*.tex form
      sources, fill.py / fill-doc, and the LaTeX-only deps) — kept for now so
      the two can be compared side by side.
- [ ] Polish HTML output: signature underlines length, exact header letter-
      spacing vs the official PDF, long-email wrapping.
- [ ] Make the remaining skeleton docs (safety-briefing, shopping/packing-list,
      yacht-log, yacht-check-in) into HTML templates + models if wanted.
- [ ] Make the other skeleton docs (safety-briefing, shopping-list, packing-list,
      yacht-log, yacht-check-in) into real fillable forms + models, if wanted.
