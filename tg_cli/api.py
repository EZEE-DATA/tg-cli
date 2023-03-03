from typing import Any, List

from telethon import TelegramClient
from telethon.types import Channel
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest

from tg_cli.models import IChannel


def one_time_request(f):
    async def wrapped(*args, **kwargs):
        for a in args:
            if isinstance(a, TelegramClient):
                client = a
                break
        else:
            client = kwargs.get("client")

        if not isinstance(client, TelegramClient):
            raise ValueError()

        await client.connect()
        result = await f(*args, **kwargs)

        keep_connection = kwargs.get("keep_connection")

        if not keep_connection:
            await client.disconnect()

        return result

    return wrapped


@one_time_request
async def get_entity_by_url(client: TelegramClient, url: str, keep_connection=False) -> Any:
    """ Возвращает некое Entity (канал, чат, пользователь) на основе ссылки на входе """
    return await client.get_entity(url)


@one_time_request
async def leave_channel(client: TelegramClient, channel_id: int, keep_connection=False) -> None:
    """ Отписаться от канала """
    channel_entity = await get_followed_channel(client, channel_id, keep_connection=True)
    await client(LeaveChannelRequest(channel_entity))


@one_time_request
async def join_channel(client: TelegramClient, channel_url: str, keep_connection=False) -> IChannel:
    """ Подписаться на канал """
    channel_entity = await get_entity_by_url(client, channel_url, keep_connection=True)
    await client(JoinChannelRequest(channel_entity))
    return IChannel.from_telethon(channel_entity)


@one_time_request
async def get_messages(client: TelegramClient, id: int,  amount: int, reference_id: int = None, wait_time: int = None, keep_connection=False):
    """ Возвращает сообщения определенного канала по его URL """
    channel_entity = await get_followed_channel(client, id, keep_connection=True)

    if channel_entity is None:
        raise ValueError(f"You are not the participant of this channel ({id=}). Join it before downloading messages")

    print(f"Retrieving messages... {channel_entity.id=} {channel_entity.title=}")

    if reference_id is not None:
        messages = [m async for m in client.iter_messages(channel_entity, min_id=reference_id, limit=amount, wait_time=wait_time)]
    else:
        messages = [m async for m in client.iter_messages(channel_entity, limit=amount, wait_time=wait_time)]

    return messages


@one_time_request
async def list_channels(client: TelegramClient, keep_connection=False) -> List[Channel]:
    channels = [d.entity async for d in client.iter_dialogs() if hasattr(d, "entity") and type(d.entity) == Channel]
    return channels


@one_time_request
async def get_followed_channel(client: TelegramClient, id: int, keep_connection=False):
    channels = await list_channels(client, keep_connection=True)
    for c in channels:
        if c.id == id:
            return c
    return None
