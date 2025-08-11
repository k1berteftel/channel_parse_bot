from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()
    get_parse_channels = State()
    get_send_channels = State()
    get_hour_range = State()
    confirm_add_channel = State()

    del_parse_channels = State()
    del_send_channels = State()

    watch_channels = State()


class adminSG(StatesGroup):
    start = State()
    get_mail = State()
    get_time = State()
    get_keyboard = State()
    confirm_mail = State()
    deeplink_menu = State()
    deeplink_del = State()
    admin_menu = State()
    admin_del = State()
    admin_add = State()
