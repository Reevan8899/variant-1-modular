# Архитектура менеджера заметок

В слое `presentation` CLI преобразует аргументы в вызовы `NoteService` и выводит результат. Сервис из `application` координирует операции. `domain` содержит `Note`, `Tag`, правила валидации, ошибки и контракт `NoteRepository`. Конкретный адаптер SQLite находится в `infrastructure`. При запуске CLI передаёт адаптер сервису через конструктор.

В SQLite отношение многие-ко-многим хранится в таблице `note_tags`. Запись заметки и её тегов проходит одной транзакцией. Тесты сервиса подставляют объект с интерфейсом `NoteRepository`, а интеграционные тесты используют временный файл.

## C4. Контейнеры

```mermaid
flowchart LR
    U["Владелец заметок<br/>[Person]"]
    subgraph System["Менеджер заметок"]
        C["Менеджер заметок CLI<br/>[Container: Python / argparse]<br/>Проверяет ввод и выполняет операции"]
        S[("База заметок<br/>[Container: SQLite]<br/>Заметки, теги, связи")]
    end
    U -->|"Вводит команды и читает результат"| C
    C -->|"Читает и пишет через sqlite3"| S
```

## C4. Компоненты прикладного слоя

```mermaid
flowchart LR
    UI["CLI<br/>[Component: presentation]"]
    subgraph App["Прикладной слой контейнера Python"]
        N["NoteService<br/>[Component: application]<br/>Координирует операции"]
        Q["Поиск заметок<br/>[Component: use_cases]<br/>Фильтрует по тексту и тегу"]
    end
    D["Note и Tag<br/>[Component: domain]<br/>Данные и правила"]
    P["NoteRepository<br/>[Interface: domain]<br/>Контракт хранения"]
    S["SQLiteNoteRepository<br/>[Component: infrastructure]"]
    UI -->|"Вызывает методы"| N
    N -->|"Делегирует запросы"| Q
    N -->|"Создаёт и валидирует"| D
    N -->|"Читает и изменяет"| P
    Q -->|"Читает заметки"| P
    S -.->|"Реализует"| P
```

## Проверка зависимостей

`python scripts/check_layers.py` разбирает обычные и относительные импорты. `domain` может обращаться к доменным модулям, `application` — к домену. `infrastructure` реализует доменные контракты. `presentation` связывает компоненты при запуске. Скрипт запускается в CI.
