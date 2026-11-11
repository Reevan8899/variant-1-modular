import pytest

from src.domain.entities.note import Note, NoteChanges
from src.domain.exceptions.domain_errors import ValidationError


def test_note_has_normalized_fields_and_unique_tags():
    note = Note.create(" Тема ", " Текст ", ["Проект  А", "проект а", "Работа"])
    assert (note.title, note.body) == ("Тема", "Текст")
    assert note.created_at == note.updated_at
    assert [tag.name for tag in note.tags] == ["проект а", "работа"]
    assert note.tags[0].id == Note.create("Другая", "Запись", ["ПРОЕКТ А"]).tags[0].id


def test_patch_distinguishes_unchanged_tags_from_cleared_tags():
    assert NoteChanges.create("Новая", None, None).tags is None
    assert NoteChanges.create(None, None, []).tags == ()
    with pytest.raises(ValidationError):
        NoteChanges.create(None, None, None)
