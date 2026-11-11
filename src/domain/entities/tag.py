from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from src.domain.exceptions.domain_errors import ValidationError


def tag_name(value: str) -> str:
    name = " ".join(value.split()).casefold()
    if not 1 <= len(name) <= 40:
        raise ValidationError("Тег должен содержать от 1 до 40 символов.")
    return name


@dataclass(frozen=True)
class Tag:
    id: str
    name: str

    @classmethod
    def from_name(cls, name: str) -> "Tag":
        return cls(uuid5(NAMESPACE_URL, f"note-tag:{name}").hex, name)


def normalize_tags(values: list[str]) -> tuple[Tag, ...]:
    names = sorted({tag_name(value) for value in values})
    return tuple(Tag.from_name(name) for name in names)
