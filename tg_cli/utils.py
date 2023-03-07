import csv
import json
from pathlib import Path
from typing import List

from tg_cli.models import Credentials, IMessage


def get_credentials(path: Path):
    return Credentials.from_file(path)


def create_csv_channel_messages_file(path: Path):
    with open(path, 'w', newline='', encoding="utf-8") as csvfile:
        writer = get_csv_writer(csvfile)
        field_names = get_csv_file_first_row()
        writer.writerow(field_names)
    return path


def get_csv_file_first_row():
    return [field_name for field_name, _ in IMessage.__annotations__.items()]


def get_csv_writer(file):
    writer = csv.writer(file, **get_csv_options())
    return writer


def get_csv_reader(file):
    reader = csv.reader(file, **get_csv_options())
    return reader


def get_csv_options():
    return dict()


def update_csv_file(path: Path, messages: List[IMessage]):
    if not path.exists():
        print(f".csv file doesn't exist. Creating a new file at {path.absolute()}")
        write_messages_to_empty_csv_file(path, messages)
        return
    written_messages = extract_written_messages_from_csv_file(path)
    messages = unite_messages(messages, written_messages)
    write_messages_to_empty_csv_file(path, messages)
    return


def extract_written_messages_from_csv_file(path: Path):
    with open(path, 'r', newline='') as csvfile:
        reader = get_csv_reader(csvfile)
        written_messages = []
        field_names = get_csv_file_first_row()
        c = 0
        for row in reader:
            if c > 0:
                mdict = {field_names[i]: v for i, v in enumerate(row)}
                written_messages.append(IMessage.parse_obj(mdict))
            c += 1
    return written_messages


def write_messages_to_empty_csv_file(path: Path, messages: List[IMessage]):
    with open(path, 'w', newline='', encoding="utf-8") as csvfile:
        writer = get_csv_writer(csvfile)
        field_names = get_csv_file_first_row()
        writer.writerow(field_names)
        for m in sorted(messages, key=lambda x: x.id):
            mdict = json.loads(m.json())
            row = [mdict.get(field_name) for field_name in field_names]
            writer.writerow(row)


def unite_messages(list_one: List[IMessage], list_two: List[IMessage]):
    for m in list_two:
        list_one_ids = [mm.id for mm in list_one]
        if m.id not in list_one_ids:
            list_one.append(m)
    return list_one
