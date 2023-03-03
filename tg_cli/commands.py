import asyncio
from pathlib import Path

import click
from telethon import TelegramClient

from tg_cli.models import Credentials, IChannel, ContextObj, IMessage
from tg_cli.api import join_channel, list_channels, leave_channel, get_messages, get_followed_channel
from tg_cli.utils import update_csv_file


@click.group
@click.option(
    "--creds",
    type=str,
    required=True,
    help="Путь к папке с данными пользователя для авторизации"
)
@click.pass_context
def cli(ctx, creds: str):
    creds = Credentials.from_file(Path(creds))
    client = TelegramClient(
        creds.session,
        creds.client_meta.app_id,
        creds.client_meta.app_hash
    )
    ctx.obj = ContextObj(client=client)


@cli.group(
    name="channels",
)
@click.pass_context
def channels(ctx):
    pass


@channels.command(
    "join"
)
@click.argument(
    "url",
    type=str
)
@click.pass_context
def join(ctx, url: str):
    channel_entity = asyncio.run(join_channel(ctx.obj.client, url))
    click.echo(channel_entity)


@channels.command(
    "list"
)
@click.pass_context
def list_(ctx):
    channels_ = asyncio.run(list_channels(ctx.obj.client))
    for c in channels_:
        click.echo(IChannel.from_telethon(c))


@channels.command
@click.argument(
    "channel_id",
    type=int,
    required=False
)
@click.pass_context
def leave(ctx, channel_id: int):
    asyncio.run(leave_channel(ctx.obj.client, channel_id))


@channels.command(
    name="download"
)
@click.argument(
    "channel_id",
    type=int,
    required=False
)
@click.option(
    "--csv",
    type=str,
    help="Путь к .csv файлу куда будет сохраняться информация (по умолчанию: WORKDIR/<id_канала>_<title_канала>.csv)",
)
@click.option(
    "--amount",
    type=int,
    help="Количество сообщений, которые нужно будет выгрузить",
    default=100,
    show_default=True
)
@click.option(
    "--min-id",
    type=int,
    help="ID сообщения с которого начинается выгрузка",
    default=1,
    show_default=True
)
@click.option(
    "--wait-time",
    type=int,
    help="Задержка при выгрузке для избежания блокировки со стороны API",
)
@click.pass_context
def download(ctx, amount: int, wait_time: int, channel_id: int, csv: str = None, min_id: int = 1):
    # FIXME: Грузить пачками и отмечать прогресс

    loop = asyncio.get_event_loop()
    messages = loop.run_until_complete(get_messages(ctx.obj.client, channel_id, amount=amount, wait_time=wait_time, reference_id=min_id))
    imessages = [IMessage.from_telethon(m) for m in messages]
    channel_entity = loop.run_until_complete(get_followed_channel(ctx.obj.client, channel_id))

    if csv is None:
        csv = Path(f"{channel_entity.id}_{channel_entity.title}.csv")
        click.echo(f".csv file is not defined, defaulting to {csv.absolute()}")

    click.echo(f"Writing to a .csv file")
    update_csv_file(Path(csv), imessages)
