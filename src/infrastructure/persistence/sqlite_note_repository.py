import sqlite3
from contextlib import closing, contextmanager
from itertools import groupby
from pathlib import Path

from src.domain.entities.note import Note, NoteChanges
from src.domain.entities.tag import Tag
from src.domain.exceptions.domain_errors import NoteNotFoundError, StorageError

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tags (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS note_tags (
    note_id TEXT REFERENCES notes(id) ON DELETE CASCADE,
    tag_id TEXT REFERENCES tags(id), PRIMARY KEY (note_id, tag_id)
);
"""

LIST_NOTES = """
SELECT n.*, t.id AS tag_id, t.name AS tag_name
FROM notes n
LEFT JOIN note_tags nt ON nt.note_id = n.id
LEFT JOIN tags t ON t.id = nt.tag_id
ORDER BY n.created_at DESC, n.id, t.name
"""


class SQLiteNoteRepository:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def _connection(self):
        try:
            with closing(sqlite3.connect(self.path)) as connection:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript(SCHEMA)
                with connection:
                    yield connection
        except sqlite3.Error as error:
            raise StorageError("Хранилище SQLite недоступно. Проверьте путь и формат файла.") from error

    def add(self, note: Note) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO notes VALUES (?, ?, ?, ?, ?)",
                (note.id, note.title, note.body, note.created_at, note.updated_at),
            )
            _insert_tags(connection, note.id, note.tags)

    def list_all(self) -> list[Note]:
        with self._connection() as connection:
            return [_note_from_rows(list(rows)) for _, rows in groupby(connection.execute(LIST_NOTES), lambda row: row["id"])]

    def update(self, note_id: str, changes: NoteChanges) -> None:
        with self._connection() as connection:
            result = connection.execute(
                "UPDATE notes SET title=COALESCE(?, title), body=COALESCE(?, body), updated_at=? WHERE id=?",
                (changes.title, changes.body, changes.updated_at, note_id),
            )
            if result.rowcount == 0:
                raise NoteNotFoundError(note_id)
            if changes.tags is not None:
                connection.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
                _insert_tags(connection, note_id, changes.tags)
                _prune_tags(connection)

    def delete(self, note_id: str) -> None:
        with self._connection() as connection:
            result = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            if result.rowcount == 0:
                raise NoteNotFoundError(note_id)
            _prune_tags(connection)


def _insert_tags(connection, note_id: str, tags: tuple[Tag, ...]) -> None:
    for tag in tags:
        connection.execute("INSERT OR IGNORE INTO tags VALUES (?, ?)", (tag.id, tag.name))
        connection.execute("INSERT INTO note_tags VALUES (?, ?)", (note_id, tag.id))


def _prune_tags(connection) -> None:
    connection.execute("DELETE FROM tags WHERE NOT EXISTS (SELECT 1 FROM note_tags WHERE tag_id = tags.id)")


def _note_from_rows(rows: list[sqlite3.Row]) -> Note:
    row = rows[0]
    tags = tuple(Tag(item["tag_id"], item["tag_name"]) for item in rows if item["tag_id"] is not None)
    return Note(row["id"], row["title"], row["body"], row["created_at"], row["updated_at"], tags)
