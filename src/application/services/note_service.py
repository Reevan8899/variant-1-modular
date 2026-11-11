from src.application.use_cases.search_notes import by_tag, by_text
from src.domain.entities.note import Note, NoteChanges
from src.domain.repositories.note_repository import NoteRepository


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def add_note(self, title: str, body: str, tags: list[str]) -> Note:
        note = Note.create(title, body, tags)
        self.repository.add(note)
        return note

    def list_notes(self) -> list[Note]:
        return self.repository.list_all()

    def search_notes(self, query: str) -> list[Note]:
        return by_text(self.repository, query)

    def search_tag(self, tag: str) -> list[Note]:
        return by_tag(self.repository, tag)

    def edit_note(self, note_id: str, title: str | None, body: str | None, tags: list[str] | None) -> None:
        self.repository.update(note_id, NoteChanges.create(title, body, tags))

    def delete_note(self, note_id: str) -> None:
        self.repository.delete(note_id)
