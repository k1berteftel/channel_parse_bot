from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters

from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        Const('Главное меню'),
        Column(
            SwitchTo(Const('Добавить канал'), id='get_parse_channels_switcher', state=startSG.get_parse_channels),
            SwitchTo(Const('Удалить канал'), id='del_parse_channels_switcher', state=startSG.del_parse_channels),
            SwitchTo(Const('Просмотреть каналы'), id='show_channels_switcher', state=startSG.watch_channels),
        ),
        state=startSG.start
    ),
    Window(
        Const('Выберите каналы из которых нужно прекратить перессылку сообщений'),
        Group(
            Select(
                Format('{item[0]}'),
                id='del_parse_channels_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_parse_channel_selector
            ),
            width=1
        ),
        Column(
            Button(Const('Удалить выбранные каналы'), id='del_parse_channels', on_click=getters.del_parse_channels),
            SwitchTo(Const('Дальше'), id='del_parse_channels_getter', state=startSG.del_send_channels),
        ),
        SwitchTo(Const('Назад'), id='back', state=startSG.start),
        getter=getters.del_parse_channels_getter,
        state=startSG.del_parse_channels
    ),
    Window(
        Const('Выберите каналы в которые нужно прекратить перессылку сообщений'),
        Group(
            Select(
                Format('{item[0]}'),
                id='del_send_channels_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_send_channel_selector
            ),
            width=1
        ),
        Column(
            Button(Const('Удалить выбранные каналы'), id='del_send_channels', on_click=getters.del_send_channels),
        ),
        SwitchTo(Const('Назад'), id='back_del_parse_channels', state=startSG.del_parse_channels),
        getter=getters.del_send_channels_getter,
        state=startSG.del_send_channels
    ),
    Window(
        Const('Введите канал(ы) из которых будут пересылаться посты\n\nДопустимый '
              'формат ввода (каналы разделяются абзацами):\n'
              'https://t.me/room_RO (ссылка)\n@room_RO (юзернейм)\n-1001053645184 (ID)'),
        TextInput(
            id='get_parse_channels',
            on_success=getters.get_parse_channels
        ),
        SwitchTo(Const('Назад'), id='back', state=startSG.start),
        disable_web_page_preview=True,
        state=startSG.get_parse_channels
    ),
    Window(
        Const('Введите канал(ы) в которые будут пересылаться посты\n\nДопустимый '
              'формат ввода (каналы разделяются абзацами):\n'
              'https://t.me/room_RO (ссылка)\n@room_RO (юзернейм)\n-1001053645184 (ID)'),
        TextInput(
            id='get_send_channels',
            on_success=getters.get_send_channels
        ),
        SwitchTo(Const('Назад'), id='back_get_parse_channels', state=startSG.get_parse_channels),
        disable_web_page_preview=True,
        state=startSG.get_send_channels
    ),
    Window(
        Const('Введите количество часов для рандома перессылки (н-р: 1-23)'),
        TextInput(
            id='get_hour_range',
            on_success=getters.get_hour_range
        ),
        SwitchTo(Const('Назад'), id='back_get_send_channels', state=startSG.get_send_channels),
        state=startSG.get_hour_range
    ),
    Window(
        Format('<b>Посты будут перессылаться из канала(ов)</b>: {parse_channels}\n'
               '<b>В канал:</b>{send_channels}\n С временным разбросом {hour_range} часов'),
        Column(
            Button(Const('Подтвердить'), id='save_channels', on_click=getters.save_channels),
            Button(Const('Отменить'), id='cancel_save', on_click=getters.cancel_save),
        ),
        SwitchTo(Const('Назад'), id='back_get_hour_range', state=startSG.get_hour_range),
        getter=getters.confirm_add_channels_getter,
        state=startSG.confirm_add_channel
    ),
    Window(
        Format('{text}'),
        SwitchTo(Const('Назад'), id='back', state=startSG.start),
        getter=getters.watch_channels_getter,
        state=startSG.watch_channels
    )
)