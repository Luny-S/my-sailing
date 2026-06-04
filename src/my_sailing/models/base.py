"""Base classes for fillable-document data models.

A ``FormDocument`` is a clean, human-facing pydantic model (what the input
JSON validates against). Each concrete model knows how to *adapt* itself to
the flat ``{field_name: value}`` mapping that the AcroForm in the compiled PDF
uses — see :meth:`FormDocument.to_form_fields` / :meth:`to_copies`.
"""

from __future__ import annotations

from abc import abstractmethod

from pydantic import BaseModel, ConfigDict, model_validator


class Bilingual(BaseModel):
    """A value whose text differs by language (e.g. a certificate name).

    Accepts either a plain string (used for both languages) or ``{pl, en}``::

        "cert": "JSM"                              # same in both
        "cert": {"pl": "Jachtowy Sternik Morski",  # different per language
                 "en": "Yachtmaster Offshore"}
    """

    model_config = ConfigDict(extra="forbid")

    pl: str | None = None
    en: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _from_scalar(cls, value):
        if isinstance(value, str):
            return {"pl": value, "en": value}
        return value

    def __bool__(self) -> bool:
        return bool(self.pl or self.en)


class FormDocument(BaseModel):
    """A document whose data can be flattened to PDF form fields."""

    # Reject unknown keys so typos in the input JSON are caught early.
    model_config = ConfigDict(extra="forbid")

    @abstractmethod
    def to_form_fields(self) -> dict[str, object]:
        """Return a ``{field_name: value}`` mapping for a single filled form."""
        raise NotImplementedError

    def to_copies(self) -> list[dict[str, object]]:
        """One field-mapping per output copy. Default: a single copy.

        Documents that fan out (e.g. one crew-opinion per crew member) override
        this to return one mapping per copy.
        """
        return [self.to_form_fields()]


def put(fields: dict[str, object], key: str, value: object) -> None:
    """Add ``key -> str(value)`` unless the value is empty/None."""
    if value is None:
        return
    text = str(value)
    if text.strip():
        fields[key] = text


def put_lang(fields: dict[str, object], base: str, value: Bilingual | None) -> None:
    """Add ``base_pl`` / ``base_en`` from a :class:`Bilingual` value."""
    if value is None:
        return
    put(fields, f"{base}_pl", value.pl)
    put(fields, f"{base}_en", value.en)
