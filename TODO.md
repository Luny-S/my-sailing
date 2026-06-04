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
- [ ] **Tech decision**: keep LaTeX + AcroForm, or move to HTML+CSS (WeasyPrint)
      / Typst for data-driven print PDFs. Hinges on whether *interactive*
      fillable PDFs are needed, or only print-ready blanks + pre-filled
      (flattened) PDFs. See chat notes.
- [ ] Make the other skeleton docs (safety-briefing, shopping-list, packing-list,
      yacht-log, yacht-check-in) into real fillable forms + models, if wanted.
