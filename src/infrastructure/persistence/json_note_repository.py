"""Реализация NoteRepository для локального JSON-файла."""

import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path

from filelock import FileLock, Timeout

from src.domain.entities.note import Note, NoteChanges
from src.domain.entities.tag import Tag
from src.domain.exceptions.domain_errors import NoteNotFoundError, StorageError


class JSONNoteRepository:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.lock = FileLock(self.path.with_name(f"{self.path.name}.lock"), timeout=2)

    def list_all(self) -> list[Note]:
        try:
            with self.path.open(encoding="utf-8") as source:
                records = json.load(source)
            if not isinstance(records, list):
                raise ValueError("Expected a list of notes")
            notes = [_decode(record) for record in records]
            notes.sort(key=lambda note: note.id)
            return sorted(notes, key=lambda note: note.created_at, reverse=True)
        except FileNotFoundError:
            return []
        except (OSError, TypeError, ValueError, KeyError) as error:
            raise StorageError("Хранилище JSON недоступно. Проверьте путь и формат файла.") from error

    @contextmanager
    def _transaction(self):
        try:
            with self.lock:
                notes = self.list_all()
                yield notes
                self._write(notes)
        except (OSError, Timeout) as error:
            raise StorageError("Хранилище JSON недоступно. Проверьте права доступа и повторите операцию.") from error

    def _write(self, notes: list[Note]) -> None:
        fd, name = tempfile.mkstemp(dir=self.path.parent, prefix=".notes-", suffix=".tmp")
        temporary = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as target:
                json.dump([asdict(note) for note in notes], target, ensure_ascii=False)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)

    def add(self, note: Note) -> None:
        with self._transaction() as notes:
            notes.append(note)

    def update(self, note_id: str, changes: NoteChanges) -> None:
        with self._transaction() as notes:
            index = _index(notes, note_id)
            original = notes[index]
            notes[index] = replace(
                original,
                title=original.title if changes.title is None else changes.title,
                body=original.body if changes.body is None else changes.body,
                tags=original.tags if changes.tags is None else changes.tags,
                updated_at=changes.updated_at,
            )

    def delete(self, note_id: str) -> None:
        with self._transaction() as notes:
            del notes[_index(notes, note_id)]


def _decode(record: dict) -> Note:
    if not isinstance(record, dict):
        raise ValueError("Expected a note record")
    fields = dict(record)
    fields["tags"] = tuple(Tag(**tag) for tag in fields["tags"])
    return Note(**fields)


def _index(notes: list[Note], note_id: str) -> int:
    for index, note in enumerate(notes):
        if note.id == note_id:
            return index
    raise NoteNotFoundError(note_id)
