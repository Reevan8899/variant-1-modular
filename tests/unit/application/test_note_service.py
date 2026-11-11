from unittest.mock import Mock

import pytest

from src.application.services.note_service import NoteService
from src.domain.entities.note import Note
from src.domain.exceptions.domain_errors import ValidationError
from src.domain.repositories.note_repository import NoteRepository


@pytest.fixture
def repository():
    return Mock(spec=NoteRepository)


def test_service_stores_normalized_entity(repository):
    note = NoteService(repository).add_note(" Тема ", "Текст", ["Тег"])
    repository.add.assert_called_once_with(note)
    assert (note.title, note.tags[0].name) == ("Тема", "тег")


def test_invalid_entity_does_not_call_storage(repository):
    with pytest.raises(ValidationError):
        NoteService(repository).add_note(" ", "Текст", [])
    repository.add.assert_not_called()


def test_search_is_testable_without_sqlite(repository):
    wanted = Note.create("Тема", "Нужный текст", ["Работа"])
    other = Note.create("Книга", "Описание", [])
    repository.list_all.return_value = [wanted, other]
    service = NoteService(repository)
    assert service.search_notes("НУЖНЫЙ") == [wanted]
    assert service.search_tag("РАБОТА") == [wanted]


def test_service_passes_changes_and_id_to_repository(repository):
    service = NoteService(repository)
    service.edit_note("id", "Новая", None, [])
    note_id, changes = repository.update.call_args.args
    assert (note_id, changes.title, changes.body, changes.tags) == ("id", "Новая", None, ())
    service.delete_note("id")
    repository.delete.assert_called_once_with("id")
