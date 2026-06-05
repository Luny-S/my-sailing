"""Data model for the PZŻ *opinia z rejsu* / crew member's certificate of passage.

This document is issued **per crew member**: the shared cruise data (yacht,
voyage, hours, assessing captain) is combined with each crew member's personal
details and the captain's assessment, producing one 2-page form per member.
:meth:`CrewOpinion.to_copies` returns one field-mapping per crew member.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import Bilingual, FormDocument, put, put_lang

# choice value -> checkbox field name in crew_opinion.tex
_OPINION = {"positive": "op_opinion_pos", "negative": "op_opinion_neg"}
_DUTIES = {"very_good": "op_duties_vg", "good": "op_duties_g",
           "satisfactory": "op_duties_s", "unsatisfactory": "op_duties_u"}
_SICK = {"none": "op_sick_no", "heavy": "op_sick_heavy", "could_work": "op_sick_work"}
_ENDURANCE = {"good": "op_endur_g", "satisfactory": "op_endur_s",
              "unsatisfactory": "op_endur_u", "not_tested": "op_endur_nt"}


class CrewOpinionMember(BaseModel):
    """One crew member: personal details + the captain's assessment of them."""

    model_config = ConfigDict(extra="forbid")

    # Personal information
    name: str | None = Field(default=None, description="Imię i nazwisko")
    cert: Bilingual | None = Field(default=None, description="stop. żegl./mot. i nr pat.")
    phone: str | None = None
    email: str | None = None
    rank: Bilingual | None = Field(default=None, description="funkcja")

    # Captain's opinion (each maps to a checkbox group)
    opinion: Literal["positive", "negative"] | None = None
    duties: Literal["very_good", "good", "satisfactory", "unsatisfactory"] | None = None
    seasickness: Literal["none", "heavy", "could_work"] | None = None
    endurance: Literal["good", "satisfactory", "unsatisfactory", "not_tested"] | None = None

    remarks: Bilingual | None = Field(default=None, description="UWAGI KAPITANA")

    def has_content(self) -> bool:
        return any([self.name, self.cert, self.rank, self.opinion, self.duties,
                    self.seasickness, self.endurance, self.remarks])


class CrewOpinion(FormDocument):
    """Opinia z rejsu / Crew member's certificate of passage (one per member)."""

    # --- Yacht (shared) ---
    yacht_reg: str | None = None
    yacht_name: str | None = None
    yacht_loa: str | None = None
    yacht_homeport: str | None = None
    yacht_engine: str | None = None

    # --- Cruise (shared) ---
    logbook_no: str | None = None
    port_embark: str | None = None
    date_embark: str | None = None
    port_disembark: str | None = None
    date_disembark: str | None = None
    visited_ports: str | None = None
    tidal_ports_count: str | None = None
    cruise_days: str | None = None

    # --- Hours / distance (shared) ---
    hours_total: str | None = None
    hours_sails: str | None = None
    hours_engine: str | None = None
    hours_tidal: str | None = None
    hours_mooring: str | None = None
    trip_nm: str | None = None

    # --- Assessing captain (shared) ---
    captain_name: str | None = None
    captain_cert: Bilingual | None = None
    captain_phone: str | None = None
    captain_email: str | None = None
    captain_place_date: str | None = None

    # --- Crew: one output form is produced per member ---
    crew: list[CrewOpinionMember] = Field(default_factory=list)

    def _shared_fields(self) -> dict[str, object]:
        f: dict[str, object] = {}
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

        put(f, "cap_name", self.captain_name)
        put_lang(f, "cap_cert", self.captain_cert)
        put(f, "cap_phone", self.captain_phone)
        put(f, "cap_email", self.captain_email)
        put(f, "cap_place_date", self.captain_place_date)
        return f

    def _member_fields(self, member: CrewOpinionMember) -> dict[str, object]:
        f = self._shared_fields()
        put(f, "part_name", member.name)
        put_lang(f, "part_cert", member.cert)
        put(f, "part_phone", member.phone)
        put(f, "part_email", member.email)
        put_lang(f, "part_rank", member.rank)

        for value, mapping in (
            (member.opinion, _OPINION), (member.duties, _DUTIES),
            (member.seasickness, _SICK), (member.endurance, _ENDURANCE),
        ):
            if value is not None:
                f[mapping[value]] = True

        put_lang(f, "remarks_captain", member.remarks)
        return f

    def print_members(self) -> list[CrewOpinionMember | None]:
        """Members to print one form each (a single blank form if none)."""
        real = [m for m in self.crew if m.has_content()]
        return real or [None]

    def to_copies(self) -> list[dict[str, object]]:
        members = [m for m in self.crew if m.has_content()]
        if not members:
            return [self._shared_fields()]  # one blank-participant form
        return [self._member_fields(m) for m in members]

    def to_form_fields(self) -> dict[str, object]:
        # A representative single mapping (first member, else shared only).
        return self.to_copies()[0]
