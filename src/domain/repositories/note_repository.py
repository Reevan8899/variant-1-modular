from typing import Protocol

from src.domain.entities.note import Note, NoteChanges


class NoteRepository(Protocol):
    """Контракт хранения заметок для прикладного слоя."""

    def add(self, note: Note) -> None: ...

    def list_all(self) -> list[Note]: ...

    def update(self, note_id: str, changes: NoteChanges) -> None: ...

    def delete(self, note_id: str) -> None: ...
