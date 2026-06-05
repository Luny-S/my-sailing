"""Minimal models for blank / static print forms.

Content (checklist items, procedure steps) lives directly in the HTML
templates so it is easy to edit without touching Python code.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .base import FormDocument


class BlankForm(FormDocument):
    """Blank print form with optional header fields.

    Used for: safety-briefing, checklista, lista-skippera.
    """

    model_config = ConfigDict(extra="forbid")

    yacht: str | None = None
    date: str | None = None

    def to_form_fields(self) -> dict[str, object]:
        return {}


class CrewListMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    phone: str | None = None


class CrewList(FormDocument):
    """Crew contact list — A5 format, one row per member."""

    model_config = ConfigDict(extra="forbid")

    yacht: str | None = None
    date: str | None = None
    crew: list[CrewListMember] = []

    def to_form_fields(self) -> dict[str, object]:
        return {}


class MaydayCard(FormDocument):
    """Pre-filled MAYDAY / MIPDANIO call card."""

    model_config = ConfigDict(extra="forbid")

    yacht_name: str | None = None
    mmsi: str | None = None
    call_sign: str | None = None
    channel: str = "16"

    def to_form_fields(self) -> dict[str, object]:
        return {}
