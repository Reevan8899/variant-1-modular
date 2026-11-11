from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.entities.tag import Tag, normalize_tags
from src.domain.exceptions.domain_errors import ValidationError


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def required(value: str, field: str, maximum: int) -> str:
    cleaned = value.strip()
    if not 1 <= len(cleaned) <= maximum:
        raise ValidationError(f"{field} должен содержать от 1 до {maximum} символов.")
    return cleaned


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    body: str
    created_at: str
    updated_at: str
    tags: tuple[Tag, ...]

    @classmethod
    def create(cls, title: str, body: str, tags: list[str]) -> "Note":
        timestamp = now()
        return cls(uuid4().hex, required(title, "Заголовок", 100), required(body, "Текст", 10_000), timestamp, timestamp, normalize_tags(tags))


@dataclass(frozen=True)
class NoteChanges:
    title: str | None
    body: str | None
    tags: tuple[Tag, ...] | None
    updated_at: str

    @classmethod
    def create(cls, title: str | None, body: str | None, tags: list[str] | None) -> "NoteChanges":
        if title is None and body is None and tags is None:
            raise ValidationError("Укажите хотя бы одно изменение.")
        return cls(
            None if title is None else required(title, "Заголовок", 100),
            None if body is None else required(body, "Текст", 10_000),
            None if tags is None else normalize_tags(tags),
            now(),
        )
