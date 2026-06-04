"""Base class for fillable-document data models.

A ``FormDocument`` is a clean, human-facing pydantic model (what the input
JSON validates against). Each concrete model knows how to *adapt* itself to
the flat ``{latex_field_name: value}`` mapping that the AcroForm in the
compiled PDF actually uses — see :meth:`FormDocument.to_form_fields`.
"""

from __future__ import annotations

from abc import abstractmethod

from pydantic import BaseModel, ConfigDict


class FormDocument(BaseModel):
    """A document whose data can be flattened to PDF form fields."""

    # Reject unknown keys so typos in the input JSON are caught early.
    model_config = ConfigDict(extra="forbid")

    @abstractmethod
    def to_form_fields(self) -> dict[str, str]:
        """Return a ``{latex_field_name: value}`` mapping for the PDF form."""
        raise NotImplementedError


def put(fields: dict[str, str], key: str, value: object) -> None:
    """Add ``key -> str(value)`` to ``fields`` unless the value is empty/None."""
    if value is None:
        return
    text = str(value)
    if text.strip():
        fields[key] = text
