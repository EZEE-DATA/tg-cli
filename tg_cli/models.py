import json
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

from pydantic import BaseModel, validator, ValidationError
from telethon import TelegramClient
from telethon.sessions.sqlite import SQLiteSession
from telethon.types import Channel, Message


class ContextObj(BaseModel):
    client: TelegramClient

    class Config:
        arbitrary_types_allowed = True


class ClientMetaInfo(BaseModel):
    app_id: int
    app_hash: str

    @classmethod
    def from_file(cls, path: Path):
        try:
            with open(path) as file:
                content = json.load(file)
        except FileNotFoundError as e:
            print(f"Файл с мета информацией о пользователе отсутствует: {path.absolute()}")
            raise e
        except Exception as e:
            print(f"Не удалось прочитать файл с мета информацией о пользователе: {path.absolute()}")
            raise e
        return cls.parse_obj(content)


class Credentials(BaseModel):
    path: Path
    client_meta: ClientMetaInfo
    session: SQLiteSession

    @classmethod
    @validator("session")
    def validate_session(cls, value):
        try:
            SQLiteSession(value)
        except Exception as e:
            raise ValidationError(f"Не удалось десериализовать сессию:\n{e}")
        return SQLiteSession(value)

    @classmethod
    def from_file(cls, path: Path):
        """
        Создаёт модель кредов из папки с кредами

        :param path: Путь к директории c кредами
        :return: модель кредов
        """

        client_id = path.name  # подразумевается, что все необходимые файлы названы идентификатором пользователя

        if not path.is_dir():
            raise FileNotFoundError(f"Не найдена папка с данными для авторизации: {path.absolute()}")

        client_meta_path, session_path = path / f"{client_id}.json", path / f"{client_id}.session"

        client_meta = ClientMetaInfo.from_file(client_meta_path)
        session = SQLiteSession(str(session_path.absolute()))

        return cls(
            path=path,
            client_meta=client_meta,
            session=session
        )

    class Config:
        arbitrary_types_allowed = True


class IChannel(BaseModel):
    id: int
    title: str
    username: str
    verified: bool
    participants: Optional[int]

    @classmethod
    def from_telethon(cls, obj: Channel):
        return cls(
            id=obj.id,
            title=obj.title,
            username=obj.username,
            verified=obj.verified,
            participants=obj.participants_count
        )


class IMessage(BaseModel):
    id: int
    message: Optional[str]
    date: Optional[datetime]
    views: Optional[Union[int, str]]
    forwards: Optional[Union[int, str]]

    @classmethod
    def from_telethon(cls, obj: Message):
        return cls(
            id=obj.id,
            message=obj.message,
            date=obj.date,
            views=obj.views,
            forwards=obj.forwards
        )