"""Master voyage record — single source of truth for all documents.

Fill one VoyageRecord JSON and call split() to derive each document's
data dict.  The split() result can be passed directly to render_document()
or written as individual JSON files with the ``render-voyage --split``
command.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import Bilingual


# ------------------------------------------------------------------ helpers

def _bi(v: Bilingual | None) -> dict | str | None:
    """Serialize a Bilingual value for a sub-document dict.

    If both sides are identical the value is simplified to a plain string
    so the output JSON stays readable.
    """
    if v is None:
        return None
    if v.pl == v.en:
        return v.pl or None
    d = {k: val for k, val in {"pl": v.pl, "en": v.en}.items() if val is not None}
    return d or None


def _clean(d: dict) -> dict:
    """Strip None values (keeps empty lists / empty strings if present)."""
    return {k: v for k, v in d.items() if v is not None}


# ------------------------------------------------------------------ sub-models

class VoyageYacht(BaseModel):
    """Yacht identification and radio data."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    reg: str | None = None              # registration number
    loa: str | None = None              # LOA [m]
    homeport: str | None = None
    engine: str | None = None           # engine power [kW]
    mmsi: str | None = None             # for MAYDAY card
    call_sign: str | None = None        # VHF call sign
    vhf_channel: str = "16"             # working / distress channel


class VoyageCaptain(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    cert: Bilingual | None = None       # sailing / motor certificate
    phone: str | None = None
    email: str | None = None
    place_date: str | None = None       # place + date for signature line


class VoyageCruise(BaseModel):
    """Cruise details (passage-card / crew-opinion voyage section)."""

    model_config = ConfigDict(extra="forbid")

    logbook_no: str | None = None
    port_embark: str | None = None
    date_embark: str | None = None      # also used as generic 'date' for blank forms
    port_disembark: str | None = None
    date_disembark: str | None = None
    visited_ports: str | None = None
    tidal_ports_count: str | None = None
    cruise_days: str | None = None
    hours_total: str | None = None
    hours_sails: str | None = None
    hours_engine: str | None = None
    hours_tidal: str | None = None
    hours_mooring: str | None = None
    trip_nm: str | None = None
    remarks_captain: Bilingual | None = None   # captain's overall cruise remarks
    remarks_owner: Bilingual | None = None
    owner_place_date: str | None = None


class VoyageCrewMember(BaseModel):
    """One crew member — all fields used across all documents.

    Crew-opinion assessment fields (opinion, duties, …) are optional:
    leave them blank when only crew-list / passage-card data is needed.
    """

    model_config = ConfigDict(extra="forbid")

    # common — passage-card, crew-opinion, crew-list
    name: str | None = None
    cert: Bilingual | None = None       # sailing / motor certificate
    rank: Bilingual | None = None       # function on yacht
    phone: str | None = None
    email: str | None = None

    # crew-opinion assessments (leave None if not filling opinion forms)
    opinion: Literal["positive", "negative"] | None = None
    duties: Literal["very_good", "good", "satisfactory", "unsatisfactory"] | None = None
    seasickness: Literal["none", "heavy", "could_work"] | None = None
    endurance: Literal["good", "satisfactory", "unsatisfactory", "not_tested"] | None = None
    remarks: Bilingual | None = None    # captain's per-member remarks


# ------------------------------------------------------------------ master record

class VoyageRecord(BaseModel):
    """Master record holding all voyage and crew information.

    Example usage::

        record = VoyageRecord.model_validate_json(Path("voyage.json").read_text())
        docs = record.split()
        # docs["passage-card"] → dict ready for PassageCard.model_validate()
        # docs["crew-list"]    → dict ready for CrewList.model_validate()
        # …

    Use ``render-voyage voyage.json -o output/`` to render all PDFs at once,
    or ``render-voyage voyage.json --split -o data/`` to write individual
    JSON files.
    """

    model_config = ConfigDict(extra="forbid")

    date: str | None = None         # generic date override for blank forms
                                    # (falls back to cruise.date_embark)
    yacht: VoyageYacht = Field(default_factory=VoyageYacht)
    captain: VoyageCaptain = Field(default_factory=VoyageCaptain)
    cruise: VoyageCruise = Field(default_factory=VoyageCruise)
    crew: list[VoyageCrewMember] = []

    # ------------------------------------------------------------------ private

    def _date(self) -> str | None:
        return self.date or self.cruise.date_embark

    def _passage_card_data(self) -> dict:
        crew = [
            _clean({"name": m.name, "cert": _bi(m.cert), "rank": _bi(m.rank)})
            for m in self.crew
        ]
        return _clean({
            "captain_name": self.captain.name,
            "captain_cert": _bi(self.captain.cert),
            "captain_phone": self.captain.phone,
            "captain_email": self.captain.email,
            "yacht_reg": self.yacht.reg,
            "yacht_name": self.yacht.name,
            "yacht_loa": self.yacht.loa,
            "yacht_homeport": self.yacht.homeport,
            "yacht_engine": self.yacht.engine,
            "logbook_no": self.cruise.logbook_no,
            "port_embark": self.cruise.port_embark,
            "date_embark": self.cruise.date_embark,
            "port_disembark": self.cruise.port_disembark,
            "date_disembark": self.cruise.date_disembark,
            "visited_ports": self.cruise.visited_ports,
            "tidal_ports_count": self.cruise.tidal_ports_count,
            "cruise_days": self.cruise.cruise_days,
            "hours_total": self.cruise.hours_total,
            "hours_sails": self.cruise.hours_sails,
            "hours_engine": self.cruise.hours_engine,
            "hours_tidal": self.cruise.hours_tidal,
            "hours_mooring": self.cruise.hours_mooring,
            "trip_nm": self.cruise.trip_nm,
            "crew": crew if crew else None,
            "remarks_captain": _bi(self.cruise.remarks_captain),
            "captain_place_date": self.captain.place_date,
            "remarks_owner": _bi(self.cruise.remarks_owner),
            "owner_place_date": self.cruise.owner_place_date,
        })

    def _crew_opinion_data(self) -> dict:
        crew = [
            _clean({
                "name": m.name,
                "cert": _bi(m.cert),
                "rank": _bi(m.rank),
                "phone": m.phone,
                "email": m.email,
                "opinion": m.opinion,
                "duties": m.duties,
                "seasickness": m.seasickness,
                "endurance": m.endurance,
                "remarks": _bi(m.remarks),
            })
            for m in self.crew
        ]
        return _clean({
            "yacht_reg": self.yacht.reg,
            "yacht_name": self.yacht.name,
            "yacht_loa": self.yacht.loa,
            "yacht_homeport": self.yacht.homeport,
            "yacht_engine": self.yacht.engine,
            "logbook_no": self.cruise.logbook_no,
            "port_embark": self.cruise.port_embark,
            "date_embark": self.cruise.date_embark,
            "port_disembark": self.cruise.port_disembark,
            "date_disembark": self.cruise.date_disembark,
            "visited_ports": self.cruise.visited_ports,
            "tidal_ports_count": self.cruise.tidal_ports_count,
            "cruise_days": self.cruise.cruise_days,
            "hours_total": self.cruise.hours_total,
            "hours_sails": self.cruise.hours_sails,
            "hours_engine": self.cruise.hours_engine,
            "hours_tidal": self.cruise.hours_tidal,
            "hours_mooring": self.cruise.hours_mooring,
            "trip_nm": self.cruise.trip_nm,
            "captain_name": self.captain.name,
            "captain_cert": _bi(self.captain.cert),
            "captain_phone": self.captain.phone,
            "captain_email": self.captain.email,
            "captain_place_date": self.captain.place_date,
            "crew": crew if crew else None,
        })

    def _blank_form_data(self) -> dict:
        return _clean({"yacht": self.yacht.name, "date": self._date()})

    def _crew_list_data(self) -> dict:
        crew = [
            _clean({"name": m.name, "phone": m.phone})
            for m in self.crew
        ]
        return _clean({
            "yacht": self.yacht.name,
            "date": self._date(),
            "crew": crew if crew else None,
        })

    def _mayday_card_data(self) -> dict:
        return _clean({
            "yacht_name": self.yacht.name,
            "mmsi": self.yacht.mmsi,
            "call_sign": self.yacht.call_sign,
            "channel": self.yacht.vhf_channel,
        })

    # ------------------------------------------------------------------ public

    def split(self) -> dict[str, dict]:
        """Return a ``{document_name: data_dict}`` mapping for every document.

        Each value is a plain dict that can be passed directly to
        :func:`render_document` or serialised to JSON.
        """
        return {
            "passage-card":    self._passage_card_data(),
            "crew-opinion":    self._crew_opinion_data(),
            "safety-briefing": self._blank_form_data(),
            "checklista":      self._blank_form_data(),
            "lista-skippera":  {},
            "crew-list":       self._crew_list_data(),
            "mayday-card":     self._mayday_card_data(),
        }
