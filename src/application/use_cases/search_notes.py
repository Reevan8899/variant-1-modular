from src.domain.entities.note import Note, required
from src.domain.entities.tag import tag_name
from src.domain.repositories.note_repository import NoteRepository


def by_text(repository: NoteRepository, query: str) -> list[Note]:
    needle = required(query, "Запрос", 10_000).casefold()
    return [note for note in repository.list_all() if needle in note.title.casefold() or needle in note.body.casefold()]


def by_tag(repository: NoteRepository, query: str) -> list[Note]:
    target = tag_name(query)
    return [note for note in repository.list_all() if any(tag.name == target for tag in note.tags)]
