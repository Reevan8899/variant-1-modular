class DomainError(Exception):
    """Базовая ошибка менеджера заметок."""


class ValidationError(DomainError):
    """Некорректные входные данные."""


class NoteNotFoundError(DomainError):
    """В хранилище нет указанной заметки."""

    def __init__(self, note_id: str):
        super().__init__(f"Заметка {note_id} не найдена.")


class StorageError(DomainError):
    """Сбой или неверный формат хранилища."""
