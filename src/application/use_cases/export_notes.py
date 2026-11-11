import csv
from typing import TextIO

from src.domain.entities.note import Note


def export_to_csv(notes: list[Note], output: TextIO) -> None:
    writer = csv.writer(output)
    writer.writerow(["id", "title", "body", "tags"])
    for note in notes:
        writer.writerow([note.id, note.title, note.body, ", ".join(tag.name for tag in note.tags)])
