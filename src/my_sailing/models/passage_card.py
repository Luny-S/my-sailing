"""Data model for the PZŻ *karta rejsu* / captain's certificate of passage.

The public model is clean and domain-oriented (crew is a list of people).
:meth:`PassageCard.to_form_fields` adapts it to the flat AcroForm field names
used in ``documents/passage-card/passage_card.tex`` (e.g. ``crewL_1_name``).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .base import Bilingual, FormDocument, put, put_lang

MAX_CREW = 12  # two on-page tables of 6 rows each


class CrewMember(BaseModel):
    """One crew row. The ``Lp.`` ordinal is filled automatically from order.

    ``cert`` and ``rank`` are :class:`Bilingual` (their wording differs between
    the Polish and English pages); a plain string is used for both languages.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, description="Imię i nazwisko")
    cert: Bilingual | None = Field(default=None, description="stopień żegl./mot.")
    rank: Bilingual | None = Field(default=None, description="funkcja na jachcie")


class PassageCard(FormDocument):
    """Karta rejsu / Captain's certificate of passage."""

    # --- Captain ---
    captain_name: str | None = None
    captain_cert: Bilingual | None = None    # stop. żegl./mot. i nr pat.
    captain_phone: str | None = None
    captain_email: str | None = None

    # --- Yacht ---
    yacht_reg: str | None = None             # nr rej.
    yacht_name: str | None = None
    yacht_loa: str | None = None             # Lc / LOA [m]
    yacht_homeport: str | None = None
    yacht_engine: str | None = None          # moc silnika [kW]

    # --- Cruise ---
    logbook_no: str | None = None            # nr pływania
    port_embark: str | None = None
    date_embark: str | None = None
    port_disembark: str | None = None
    date_disembark: str | None = None
    visited_ports: str | None = None
    tidal_ports_count: str | None = None
    cruise_days: str | None = None

    # --- Hours / distance ---
    hours_total: str | None = None
    hours_sails: str | None = None
    hours_engine: str | None = None
    hours_tidal: str | None = None
    hours_mooring: str | None = None
    trip_nm: str | None = None

    # --- Crew (list of people; first 6 fill the left table, next 6 the right) ---
    crew: list[CrewMember] = Field(default_factory=list)

    # --- Comments / signatures (remarks wording differs by language) ---
    remarks_captain: Bilingual | None = None
    captain_place_date: str | None = None
    remarks_owner: Bilingual | None = None
    owner_place_date: str | None = None

    def to_form_fields(self) -> dict[str, object]:
        f: dict[str, object] = {}

        put(f, "cap_name", self.captain_name)
        put_lang(f, "cap_cert", self.captain_cert)
        put(f, "cap_phone", self.captain_phone)
        put(f, "cap_email", self.captain_email)

        put(f, "yacht_reg", self.yacht_reg)
        put(f, "yacht_name", self.yacht_name)
        put(f, "yacht_loa", self.yacht_loa)
        put(f, "yacht_homeport", self.yacht_homeport)
        put(f, "yacht_engine", self.yacht_engine)

        put(f, "cruise_logbook", self.logbook_no)
        put(f, "port_embark", self.port_embark)
        put(f, "date_embark", self.date_embark)
        put(f, "port_disembark", self.port_disembark)
        put(f, "date_disembark", self.date_disembark)
        put(f, "visited_ports", self.visited_ports)
        put(f, "tidal_count", self.tidal_ports_count)
        put(f, "cruise_days", self.cruise_days)

        put(f, "h_total", self.hours_total)
        put(f, "h_sails", self.hours_sails)
        put(f, "h_engine", self.hours_engine)
        put(f, "h_tidal", self.hours_tidal)
        put(f, "h_mooring", self.hours_mooring)
        put(f, "trip_nm", self.trip_nm)

        # Skip empty rows, then number the real crew consecutively (Lp.).
        real_crew = [m for m in self.crew[:MAX_CREW] if m.name or m.cert or m.rank]
        for i, member in enumerate(real_crew):
            side = "L" if i < 6 else "R"
            row = i % 6 + 1
            prefix = f"crew{side}_{row}_"
            put(f, prefix + "lp", i + 1)  # Lp. is always the position in order
            put(f, prefix + "name", member.name)
            put_lang(f, prefix + "cert", member.cert)
            put_lang(f, prefix + "rank", member.rank)

        put_lang(f, "remarks_captain", self.remarks_captain)
        put(f, "cap_place_date", self.captain_place_date)
        put_lang(f, "remarks_owner", self.remarks_owner)
        put(f, "owner_place_date", self.owner_place_date)

        return f
