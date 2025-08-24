from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from database.action_data_class import DataInteraction
from database.model import ParseChannelsTable
from config_data.config import load_config, Config
from states.state_groups import startSG


config: Config = load_config()


async def watch_channels_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channels = await session.get_channels()
    text = '<b>Список каналов:</b>\n'
    for channel in channels:
        parse_channels: list[ParseChannelsTable] = list(channel.parse_channels)
        parse_text = ', '.join([parse_channel.channel for parse_channel in parse_channels])
        text += f'{channel.channel} ◀️ {parse_text}'
    return {'text': text}


async def del_parse_channels_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    parse_channels = await session.get_parse_channels()
    buttons = []
    parse_channels_del = dialog_manager.dialog_data.get('parse_channels_del')
    if not parse_channels_del:
        parse_channels_del = []
        dialog_manager.dialog_data['parse_channels_del'] = parse_channels_del
    for channel in parse_channels:
        buttons.append(
            (
                f'✅{channel.channel}' if channel.id in parse_channels_del else channel.channel,
                channel.id
            )
        )
    return {
        'items': buttons
    }


async def del_parse_channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    parse_channels_del = dialog_manager.dialog_data.get('parse_channels_del')
    parse_channels_del.append(int(item_id))
    dialog_manager.dialog_data['parse_channels_del'] = parse_channels_del
    await dialog_manager.switch_to(startSG.del_parse_channels)


async def del_parse_channels(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    parse_channels_del = dialog_manager.dialog_data.get('parse_channels_del')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_parse_channels(parse_channels_del)
    await clb.answer('Каналы были успешно удалены')
    await dialog_manager.switch_to(startSG.del_parse_channels)


async def del_send_channels_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    send_channels = await session.get_channels()
    buttons = []
    send_channels_del = dialog_manager.dialog_data.get('send_channels_del')
    if not send_channels_del:
        send_channels_del = []
        dialog_manager.dialog_data['send_channels_del'] = send_channels_del
    for channel in send_channels:
        buttons.append(
            (
                f'✅{channel.channel}' if channel.id in send_channels_del else channel.channel,
                channel.id
            )
        )
    return {
        'items': buttons
    }


async def del_send_channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    send_channels_del = dialog_manager.dialog_data.get('send_channels_del')
    send_channels_del.append(int(item_id))
    dialog_manager.dialog_data['send_channels_del'] = send_channels_del
    await dialog_manager.switch_to(startSG.del_send_channels)


async def del_send_channels(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    send_channels_del = dialog_manager.dialog_data.get('send_channels_del')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_channels(send_channels_del)
    await clb.answer('Каналы были успешно удалены')
    await dialog_manager.switch_to(startSG.del_send_channels)


async def get_parse_channels(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    channels = text.strip().split('\n')
    parse_channels = []
    for channel in channels:
        if channel.startswith('@'):
            parse_channels.append(channel)
        if channel.startswith('https') or channel.startswith('t.me'):
            parse_channels.append('@' + channel.split('/')[-1])
        try:
            channel = int(channel)
            channel = await msg.bot.get_chat(channel)
            parse_channels.append('@' + channel.username)
        except Exception:
            ...
    if not parse_channels:
        await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['parse_channels'] = parse_channels
    await dialog_manager.switch_to(startSG.get_send_channels)


async def get_send_channels(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    channels = text.strip().split('\n')
    send_channels = []
    for channel in channels:
        if channel.startswith('@'):
            send_channels.append(channel)
        if channel.startswith('https') or channel.startswith('t.me'):
            send_channels.append('@' + channel.split('/')[-1])
        try:
            channel = int(channel)
            channel = await msg.bot.get_chat(channel)
            send_channels.append('@' + channel.username)
        except Exception:
            ...
    if not send_channels:
        await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['send_channels'] = send_channels
    await dialog_manager.switch_to(startSG.get_hour_range)


async def get_hour_range(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        hours = text.strip().split('-')
        min_hour, max_hour = int(hours[0].strip()), int(hours[1].strip())
    except Exception:
        await msg.answer('Вы ввели данные не том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['min_hour'] = min_hour
    dialog_manager.dialog_data['max_hour'] = max_hour
    await dialog_manager.switch_to(startSG.confirm_add_channel)


async def select_no_range(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['min_hour'] = 0
    dialog_manager.dialog_data['max_hour'] = 0
    await dialog_manager.switch_to(startSG.confirm_add_channel)


async def confirm_add_channels_getter(dialog_manager: DialogManager, **kwargs):
    parse_channels = dialog_manager.dialog_data.get('parse_channels')
    send_channels = dialog_manager.dialog_data.get('send_channels')
    min_hour = dialog_manager.dialog_data.get('min_hour')
    max_hour = dialog_manager.dialog_data.get('max_hour')

    parse_channels_text = ''
    for channel in parse_channels:
        parse_channels_text += f'\n{channel}'
    send_channels_text = ''
    for channel in send_channels:
        send_channels_text += f'\n{channel}'
    hours_text = f'{min_hour} - {max_hour}'
    return {
        'parse_channels': parse_channels_text,
        'send_channels': send_channels_text,
        'hour_range': hours_text
    }


async def save_channels(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    parse_channels = dialog_manager.dialog_data.get('parse_channels')
    send_channels = dialog_manager.dialog_data.get('send_channels')
    min_hour = dialog_manager.dialog_data.get('min_hour')
    max_hour = dialog_manager.dialog_data.get('max_hour')
    await session.add_channels(send_channels, parse_channels, min_hour, max_hour)
    await clb.message.answer('Каналы были успешно добавлены')
    await dialog_manager.switch_to(startSG.start, show_mode=ShowMode.DELETE_AND_SEND)


async def cancel_save(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(startSG.start)
