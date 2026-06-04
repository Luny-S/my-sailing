"""Data models and the registry of fillable documents.

A fillable document = a compiled PDF (with an AcroForm) + a pydantic model
describing its data. Look documents up by name via :data:`DOCUMENTS`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .base import Bilingual, FormDocument
from .crew_opinion import CrewOpinion, CrewOpinionMember
from .passage_card import CrewMember, PassageCard

ROOT = Path(__file__).resolve().parents[3]
BUILD_DIR = ROOT / "build"

__all__ = [
    "Bilingual",
    "FormDocument",
    "CrewMember",
    "PassageCard",
    "CrewOpinion",
    "CrewOpinionMember",
    "DocumentSpec",
    "DOCUMENTS",
    "get_document",
]


@dataclass(frozen=True)
class DocumentSpec:
    """A fillable document: its model and its compiled template PDF."""

    name: str
    title: str
    model: type[FormDocument]
    template: Path

    @property
    def template_built(self) -> bool:
        return self.template.exists()


DOCUMENTS: dict[str, DocumentSpec] = {
    "passage-card": DocumentSpec(
        name="passage-card",
        title="Karta rejsu / Captain's certificate of passage",
        model=PassageCard,
        template=BUILD_DIR / "documents" / "passage-card" / "passage_card.pdf",
    ),
    "crew-opinion": DocumentSpec(
        name="crew-opinion",
        title="Opinia z rejsu / Crew member's certificate of passage (one per member)",
        model=CrewOpinion,
        template=BUILD_DIR / "documents" / "crew-opinion" / "crew_opinion.pdf",
    ),
}


def get_document(name: str) -> DocumentSpec:
    try:
        return DOCUMENTS[name]
    except KeyError:
        known = ", ".join(sorted(DOCUMENTS)) or "(none)"
        raise KeyError(f"Unknown document '{name}'. Available: {known}") from None
