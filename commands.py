from telebot.types import BotCommand

default_commands = [
    BotCommand("start", "начало работа"),
    BotCommand("help", "помощь"),
    BotCommand("joke", "случайная шутка"),
    BotCommand("joke2", "штука с каламбуром"),
    BotCommand("jpy_to_rub", "конвертировать JPY в RUB"),
    BotCommand("cvt", "ковертировать любую валюту в другую"),
    BotCommand("set_my_currency", "установите целевую валюту"),
    BotCommand("set_local_currency", "установить локальную валюту")
]