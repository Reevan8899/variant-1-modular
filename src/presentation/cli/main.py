"""CLI менеджера заметок."""

import argparse
import os
import sys
from pathlib import Path

from src.application.services.note_service import NoteService
from src.domain.entities.note import Note
from src.domain.exceptions.domain_errors import DomainError
from src.infrastructure.persistence.json_note_repository import JSONNoteRepository
from src.infrastructure.persistence.sqlite_note_repository import SQLiteNoteRepository


class NoteParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise DomainError("Неверная команда или параметры. Откройте --help.")


def make_parser() -> NoteParser:
    parser = NoteParser(description="Менеджер заметок и тегов")
    parser.add_argument("--db", type=Path, help="Путь к файлу хранилища")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Создать заметку")
    add.add_argument("--title", required=True)
    add.add_argument("--body", required=True)
    add.add_argument("--tag", dest="tags", action="append", default=[])
    commands.add_parser("list", help="Показать все заметки")
    search = commands.add_parser("search", help="Найти заметки по тексту")
    search.add_argument("--query", required=True)
    search_tag = commands.add_parser("search-tag", help="Найти заметки по тегу")
    search_tag.add_argument("--tag", required=True)
    edit = commands.add_parser("edit", help="Изменить заметку")
    edit.add_argument("id")
    edit.add_argument("--title")
    edit.add_argument("--body")
    tags = edit.add_mutually_exclusive_group()
    tags.add_argument("--tag", dest="tags", action="append")
    tags.add_argument("--clear-tags", dest="tags", action="store_const", const=[])
    commands.add_parser("delete", help="Удалить заметку").add_argument("id")
    return parser


def print_notes(notes: list[Note]) -> None:
    if not notes:
        print("Заметки не найдены.")
        return
    print("ID | Заголовок | Теги")
    for note in notes:
        tags = ", ".join(tag.name for tag in note.tags)
        print(f"{note.id} | {note.title} | {tags}")


def main(argv: list[str] | None = None) -> int:
    try:
        args = make_parser().parse_args(argv)
        storage = os.environ.get("STORAGE", "sqlite")
        repositories = {"sqlite": (SQLiteNoteRepository, "notes.sqlite3"), "json": (JSONNoteRepository, "notes.json")}
        if storage not in repositories:
            raise DomainError("Укажите STORAGE=sqlite или STORAGE=json.")
        repository, default_path = repositories[storage]
        path = args.db or Path(os.environ.get("NOTES_FILE", default_path))
        service = NoteService(repository(path))
        match args.command:
            case "add":
                note = service.add_note(args.title, args.body, args.tags)
                print(f"Заметка создана. ID: {note.id}")
            case "list":
                print_notes(service.list_notes())
            case "search":
                print_notes(service.search_notes(args.query))
            case "search-tag":
                print_notes(service.search_tag(args.tag))
            case "edit":
                service.edit_note(args.id, args.title, args.body, args.tags)
                print(f"Заметка обновлена. ID: {args.id}")
            case "delete":
                service.delete_note(args.id)
                print(f"Заметка удалена. ID: {args.id}")
    except DomainError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
