# Практическая работа № 7. Вариант № 1

Менеджер заметок с тегами. Слоистая организация кода. [Описание архитектуры](docs/architecture.md) [Вторая реализация](https://github.com/Reevan8899/variant-1-flat)

## Модель данных

- `Note` хранит ID, заголовок, текст, даты создания и изменения, связанные теги.
- `Tag` хранит ID и нормализованное имя. Связь заметок и тегов многие-ко-многим задаёт таблица `note_tags`.

## Запуск

Нужен Python 3.10+. Хранилище по умолчанию `notes.sqlite3`. Чтобы указать другой путь, передайте `--db PATH` до команды или задайте `NOTES_FILE`.

```sh
python -m src.presentation.cli.main add --title "План" --body "Подготовить материалы" --tag Учёба --tag Срочно
python -m src.presentation.cli.main list
python -m src.presentation.cli.main search --query "МАТЕРИАЛЫ"
python -m src.presentation.cli.main search-tag --tag учёба
python -m src.presentation.cli.main edit ID --title "Обновлённый план"
python -m src.presentation.cli.main delete ID
```

Укажите фактический ID из списка. При редактировании `--tag` заменяет набор тегов, `--clear-tags` очищает его. Удаление по указанному ID выполняется сразу.

## Проверка

```sh
python -m pip install -r requirements.txt
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```
