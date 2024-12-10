from custom_filters.inline_filters import is_query_only_digits
from custom_filters.inline_filters import is_query_amount_and_available_currency
from custom_filters.inline_filters import is_query_amount_and_available_currencies_from_and_to
from custom_filters.inline_filters import any_query

from custom_filters.my_filters import current_chat_is_not_user_chat
from custom_filters.my_filters import is_hi_in_message
from custom_filters.my_filters import has_no_command_arguments
from inline_handle.any_inline_query import handle_any_inline_query
from inline_handle.currency_cvt_inline import handle_convert_query_with_selected_currency
from inline_handle.currency_cvt_inline import handle_convert_query_with_selected_currency_and_target_currency
from inline_handle.currency_cvt_inline import handle_isdigit_inline_query
from inline_handle.currency_cvt_inline import handle_convert_inline_query

import config, messages, jokes, custom_filters.my_filters as my_filters, currencies
import random as rm
from io import StringIO
from commands import default_commands
from currencies import default_currency_key
from enum import StrEnum

from telebot import custom_filters
from telebot import formatting
from telebot import util
from telebot import TeleBot, types
from telebot.handler_backends import StatesGroup, State


bot = TeleBot(config.BOT_TOKEN)

bot.add_custom_filter(custom_filters.TextMatchFilter()) # проверка на полное совпадение
#bot.add_custom_filter(custom_filters.TextContainsFilter()) # проверка на то, что слово входит в сообщения (без проверки регистров)
bot.add_custom_filter(custom_filters.ForwardFilter())
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsReplyFilter())
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.add_custom_filter(my_filters.IsUserAdminOfBot())
bot.add_custom_filter(my_filters.ContainsWordFilter())
bot.add_custom_filter(my_filters.ContainsOneOfWordFilter())
bot.add_custom_filter(my_filters.HasEntitiesFilter())

class SurveyStates(StatesGroup):
    full_name = State() # сам называет эти стейты по названию переменной
    user_email = State()
    email_newsletter = State()

any_survey_state = SurveyStates().state_list()
print(any_survey_state)

def get_yes_or_no_kb():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        )
    keyboard.add("Да", "Нет")
    return keyboard

yes_or_no_kb = get_yes_or_no_kb()

cancel_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
)
cancel_kb.add("Отмена")

# оборабочик команд

def is_valid_email(text: str) -> bool:
    return(("@" in text) and ("." in text))

def is_valid_email_message_text(message: types.Message) -> bool:
    return message.text and is_valid_email(message.text)



# блок вопроса про имя

@bot.message_handler(
        commands=["cancel"],
        state=any_survey_state,
)
@bot.message_handler(
        text=custom_filters.TextFilter(
            equals="отмена",
            ignore_case=True,
        ),
        state=any_survey_state,
)
def handle_cancel_survey(message: types.Message):
    with bot.retrieve_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
    ) as data:
        data.pop("full_name", "")
        data.pop("user_email", "")

    bot.set_state(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        state=0,
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_MESSAGE_CANCELLED,
        reply_markup=types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["survey"])
def handle_survey_command_start_survey(message: types.Message):
    bot.set_state(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        state=SurveyStates.full_name
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_MESSAGE_WELCOME_FULL_NAME,
        parse_mode="HTML",
        reply_markup=cancel_kb,
    )


@bot.message_handler(state=SurveyStates.full_name, content_types=["text"])
def handle_user_full_name(message: types.Message):
    full_name = message.text
    bot.add_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        full_name=full_name
    )
    bot.set_state(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        state=SurveyStates.user_email
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_MESSAGE_FULL_NAME_OK_AND_ASK_EMAIL.format(
            full_name=full_name
        )
    )

@bot.message_handler(state=SurveyStates.full_name, content_types=util.content_type_media)
def handle_user_full_name_not_text(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_ERROR_MESSAGE_FULL_NAME,
        parse_mode="HTML"
    )

# блок вопрос про имейл
@bot.message_handler(
    state=SurveyStates.user_email, 
    content_types=["text"], 
    func=is_valid_email_message_text,
)
def handle_user_email_ok(message: types.Message):
    bot.add_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        user_email = message.text,
    )
    bot.set_state(
        user_id = message.from_user.id,
        chat_id=message.chat.id,
        state=SurveyStates.email_newsletter
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_MESSAGE_EMAIL_OK,
        reply_markup=yes_or_no_kb,

    )

@bot.message_handler(
    state=SurveyStates.user_email, 
    content_types=util.content_type_media, 
)
def handle_user_email_not_okay(message: types.Message):
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.SURVEY_ERROR_MESSAGE_EMAIL,
            parse_mode="HTML"
        )

# блок про вопрос на любимое число

@bot.message_handler(
    state=SurveyStates.email_newsletter,
    content_types=["text"],
    text=custom_filters.TextFilter(
        equals="да",
        ignore_case=True,
    )
)
@bot.message_handler(
    state=SurveyStates.email_newsletter,
    content_types=["text"],
    text=custom_filters.TextFilter(
        equals="нет",
        ignore_case=True,
    )
)
def handle_newsletter_ok(message: types.Message):
    with bot.retrieve_data(
        user_id = message.from_user.id,
        chat_id=message.chat.id,
    ) as data:
        #full_name = data["full_name"]
        #user_email = data["user_email"]
        full_name = data.pop("full_name", "-")
        user_email = data.pop("user_email", "-@")

    number = message.text
    text = formatting.format_text(
        "Спасибо, что прошли наш опрос!",
        formatting.format_text(
            "Ваше имя:",
            formatting.hbold(full_name),
            separator=" ",
        ),
        formatting.format_text(
            "Ваш email:",
            formatting.hcode(user_email),
            separator=" ",
        ),
        formatting.format_text(
            "Подписка на рассылку:",
            formatting.hunderline(number),
            separator=" ",
        )
    )
    bot.set_state(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        state=0,
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove(),
    )

@bot.message_handler(
    state=SurveyStates.email_newsletter,
    content_types=util.content_type_media
)
def handle_email_newsletter_is_not_ok(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SURVEY_MESSAGE_INVALID_YES_OR_NO,
        reply_markup=yes_or_no_kb,
    )

# конец команды на опрос

# обработка random

def create_random_message_keyboard():
    kb = types.InlineKeyboardMarkup()
    random_org_button = types.InlineKeyboardButton(
        text="RANDOM (org)",
        url="https://www.random.org/",
    )
    ya_ru_site_button = types.InlineKeyboardButton(
        text = "yandex",
        url="https://ya.ru/"
    )
    kb.row(random_org_button, ya_ru_site_button)

    random_amount = rm.randint(100, 500 )
    switch_inline = types.InlineKeyboardButton(
        text=f"Конвертировать {random_amount}",
        switch_inline_query=f"{random_amount}", # перейти в инлайн режим в другой чат
    )
    switch_inline_current_chat = types.InlineKeyboardButton(
        text=f"Конвертировать {random_amount} JPY",
        switch_inline_query_current_chat=f"{random_amount} JPY", # перейти в инлайн режим в другой чат
    )
    kb.add(switch_inline)
    kb.add(switch_inline_current_chat)
    
    random_number = rm.randint(10, 50)
    random_number_button = types.InlineKeyboardButton(
        text=f"Число: {random_number}",
        callback_data="random-number:{}".format(random_number)
    )
    kb.add(random_number_button)
    
    another_random_number = rm.randint(100, 400)
    hidden_random_number_button = types.InlineKeyboardButton(
        text=f"Число: (скрыто)",
        callback_data="hidden-random-number:{}".format(another_random_number)
    )
    kb.add(hidden_random_number_button)
    
    return kb

@bot.message_handler(
        commands=["random"]
)
def handle_commant_random(message: types.Message):
    kb = create_random_message_keyboard()
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.RANDOM_MESSAGE_TEXT,
        reply_markup=kb,
    )

@bot.callback_query_handler(
    func=None,
    text=custom_filters.TextFilter(
        starts_with="random-number:",
    )
)
def handle_random_number_query(query: types.CallbackQuery):
    prefix, _, number = query.data.partition(":")
    text = f"Число: {number}"
    bot.answer_callback_query(
        callback_query_id=query.id,
        text=text,
    )
    
@bot.callback_query_handler(
    func=None,
    text=custom_filters.TextFilter(
        starts_with="hidden-random-number:",
    )
)
def handle_random_number_query(query: types.CallbackQuery):
    prefix, _, number = query.data.partition(":")
    text = f"Число: {number}"
    bot.answer_callback_query(
        callback_query_id=query.id,
        text=text,
        show_alert=True,
    )
    

# конец обработки random
@bot.message_handler(commands=['joke'])
def send_random_joke(message: types.Message):
    bot.send_message(message.chat.id, 
                    formatting.hcite(jokes.get_random_joke()),
                    parse_mode = "HTML"
    )

@bot.message_handler(commands=['joke2'])
def send_random_joke(message: types.Message):
    setup, delivery = jokes.get_random_joke_two()
    text = formatting.format_text(
        formatting.escape_html(setup),
        formatting.hspoiler(delivery),
    )

    bot.send_message(chat_id = message.chat.id, 
                    text = text,
                    parse_mode = "HTML",
    )

@bot.message_handler(commands=['file'])
def send_txt_file(message: types.Message):
    file_doc = types.InputFile("test.txt")
    bot.send_document(chat_id = message.chat.id, document = file_doc)

@bot.message_handler(commands = ['text', 'start'], is_forwarded = True)
def handle_forwarded_text(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = messages.DONT_FORWARD_COMMANDS
    )


@bot.message_handler(commands = ['text'])
def send_text_doc_from_memory(message: types.Message):
    file = StringIO("Привет!")
    file.write("Hello World!\n")
    file.write("Your random number is: ")
    file.write(str(rm.randint(1, 100)))
    file.seek(0)
    file_text_doc = types.InputFile(file)
    bot.send_document(
        chat_id = message.chat.id, 
        document = file_text_doc, 
        visible_file_name = "my_tests.txt")

@bot.message_handler(commands = ['me'])
def send_text_doc_from_memory(message: types.Message):
    file = StringIO()
    file.write(f"ID чата - {message.chat.id}\n")
    file.write(f"ID сообщения - {message.id}\n")
    file.write(f"ID пользователя - {message.from_user.id}\n")
    file.write(f"First name: {message.from_user.first_name}\n")
    file.write(f"Last name: {message.from_user.last_name}\n")
    file.write(f"Username: {message.from_user.username}\n")
    file.seek(0)
    file_text_doc = types.InputFile(file)
    bot.send_document(
        chat_id=message.chat.id,
        document=file_text_doc,
        visible_file_name="your_info.txt"
    )

@bot.message_handler(commands = ["dog_doc"])
def send_dog_as_doc(message: types.Message):
    photo_file = "pic\\dog.png"
    bot.send_document(chat_id = message.chat.id, document = photo_file)


@bot.message_handler(commands = ["dogs_doc"])
def send_dog_as_doc(message: types.Message):
    bot.send_document(chat_id = message.chat.id, document = config.DOGS_PIC_URL)


@bot.message_handler(commands = ["dogs"])
def send_dogs_photo(message: types.Message):
    bot.send_photo(
        chat_id = message.chat.id, 
        photo = config.DOGS_PIC_URL,
        reply_to_message_id = message.id
        )
    
@bot.message_handler(commands = ["dog"])
def send_dog_photo_from_id(message: types.Message):
    bot.send_photo(
        message.chat.id,
        photo = config.DOG_PIC_FILE_ID
        )
    

@bot.message_handler(commands = ["dog_file"])
def send_dog_photo_form_disk(message: types.Message):
    photo_file = types.InputFile("pics\\dog.png")
    msg = bot.send_photo(
        message.chat.id,
        photo = photo_file
    )

@bot.message_handler(commands = ["w"])
def send_dog_photo_form_disk(message: types.Message):
    photo_file_id = config.W_PICK_FILE_ID
    msg = bot.send_photo(
        message.chat.id,
        photo = photo_file_id
    )

@bot.message_handler(commands = ["help"])
def send_help_message(message: types.Message):
    bot.send_message(message.chat.id, messages.HELP_MESSAGE)


@bot.message_handler(commands = ["start"])
def handle_command_start(message: types.Message):
    bot.send_message(message.chat.id, 
                     messages.START_MESSAGE,
                     parse_mode="HTML"
    )

@bot.message_handler(commands = ["check_id"])
def handle_chat_id_request(message: types.Message):
    text = formatting.format_text(
            formatting.format_text(
                "Айди чата:",
                formatting.hcode(str(message.chat.id)),
                separator=" "
            ),
            formatting.format_text(
                "Айди отправителя:",
                formatting.hcode(str(message.from_user.id)),
                separator=" ", #склеить через пробел
            ),
        )
    if message.reply_to_message:
        text += formatting.format_text(
            "\nОтвечено на сообщение от",
            formatting.hcode(str(message.reply_to_message.from_user.id)),
            separator=" "
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        )

@bot.message_handler(commands = ["secret"], is_bot_admin = True)
def handle_admin_secret(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = messages.SECRET_MESSAGE_FOR_ADMIN
    )

@bot.message_handler(commands = ["secret"], is_bot_admin = False)
def handle_not_admin(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = messages.SECRET_MESSAGE_NOT_ADMIN
    )

@bot.message_handler(commands = ["md"])
def send_markdown_message(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = messages.MARKDOWN_TEXT,
        parse_mode = "MarkDownV2",
    )

@bot.message_handler(commands = ["html"])
def send_html_text(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = messages.html_text,
        parse_mode = "HTML"
    )

@bot.message_handler(commands = ["jpy_to_rub"])
def convert_jpy_to_rub(message: types.Message):
    arguments: str = util.extract_arguments(message.text)
    if not arguments:
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.CONVERT_JPY_ERROR,
            parse_mode="HTML",
        )
        return

    if not arguments.isdigit():
        text = formatting.format_text(
            formatting.format_text(
                messages.IVALID_ARGUMENT_JPY_CONVERT,
                formatting.hcode(arguments),
                separator=" ",
            ),
            messages.CONVERT_JPY_ERROR,
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode="HTML",
        )
        return
        
    jpy_amount = int(arguments)
    ratio = currencies.get_jpy_to_rub_ratio()
    rub_amount = jpy_amount * ratio

    bot.send_message(
        chat_id=message.chat.id,
        text = messages.format_jpy_to_rub_message(
            jpy_amount = jpy_amount,
            rub_amount = rub_amount
        ),
        parse_mode="HTML",
    )

@bot.message_handler(commands = ["cvt"], func=has_no_command_arguments) # если срабатывает функция, то отправляем сообщение, что что-то не так
def handle_cvt_no_arguments(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.CVT_HOW_TO,
        parse_mode="HTML",
    )

@bot.message_handler(commands=["set_my_currency"], func=has_no_command_arguments)
def handle_set_my_currency(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SET_MY_CURRENCY_HELP_MESSAGE_TEXT,
        parse_mode="HTML"
    )

def set_selected_currency(
        message: types.Message,
        data_key: str,
        set_currency_success_message: str,
):
    currency = util.extract_arguments(message.text) or ""
    if not currencies.is_currency_available(currency):
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.ERROR_NO_SUCH_CURRENCY.format(
                currency=formatting.hcode(currency),
            ),
            parse_mode="HTML"
        )
        return
    
    if (
        bot.get_state(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
        )
        is None
    ):
        bot.set_state(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            state=0,
        )

    bot.add_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        **{data_key: currency},
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=set_currency_success_message.format(
            currency=formatting.hcode(currency.upper()),
        ),
        parse_mode="HTML",
    )

@bot.message_handler(commands=["set_my_currency"])
def handle_set_my_currency(message: types.Message):
    set_selected_currency(
        message=message,
        data_key=currencies.default_currency_key,
        set_currency_success_message=messages.SET_MY_CURRENCY_SUCCESS_MESSAGE_TEXT,
    )

@bot.message_handler(commands=["set_local_currency"], func=current_chat_is_not_user_chat,)
def set_local_currency_handle_not_private_chat(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SET_LOCAL_CURRENCY_HELP_MESSAGE,
        parse_mode="HTML",
    )

@bot.message_handler(commands=["set_local_currency"], func=has_no_command_arguments)
def no_arg_to_set_loccal_currency(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SET_LOCAL_CURRENCY_HELP_MESSAGE,
        parse_mode="HTML"
    )

@bot.message_handler(commands=["set_local_currency"])
def set_local_currency(message: types.Message):
    set_selected_currency(
        message=message,
        data_key=currencies.local_currency_key,
        set_currency_success_message=messages.SET_LOCAL_CURRENCY_SUCCESS_MESSAGE
    )

@bot.message_handler(commands = ["cvt"]) # фукнция по преобразованию валюты
def handle_cvt_currency(message: types.Message):
    default_currency = "RUB" # валюта по умолчанию до ее изменения, будем считать рубль
    user_data = bot.current_states.get_data(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )

    if user_data and currencies.default_currency_key in user_data: # if user_data in user_data - проверка на None, чтобы не выдало ошибку
        default_currency = user_data[currencies.default_currency_key]

    arguments, amount, from_currency, to_currency = currencies.get_arguments_from_cvt_command(message, default_to=default_currency)
    if arguments == -1:
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.CVT_HOW_TO,
            parse_mode="HTML"
        )
        return
    
    if not amount.isdigit():
        error_text = formatting.format_text(
            messages.IVALID_ARGUMENT_JPY_CONVERT,
            formatting.hcode(arguments),
            messages.CVT_HOW_TO,
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=error_text,
            parse_mode="HTML"
        )
        return

    ratio = currencies.get_currency_ratio(
        from_currency=from_currency,
        to_currency=to_currency,
    )

    if ratio == currencies.ERROR_FETCHING_VALUE:
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.ERROR_FETCHING_CURRENCIES_TEXT,
        )
        return
    
    if ratio == currencies.ERROR_CURRENCY_NOT_FOUND:
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.ERROR_NO_SUCH_CURRENCY.format(
                currency=formatting.hcode(from_currency),
            ),
            parse_mode="HTML",
        )
        return
    
    if ratio == currencies.ERROR_SECOND_CURRENCY_NOT_FOUND:
        bot.send_message(
        chat_id=message.chat.id,
            text = messages.ERROR_NO_SUCH_CURRENCY.format(
                currency=formatting.hcode("rub")
            ),
            parse_mode="HTML",
        )
        return

    from_amount = int(amount)
    to_amount = from_amount * ratio

    bot.send_message(
        chat_id=message.chat.id,
        text=messages.format_currency_convert(
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=from_amount,
            to_amount=to_amount,
        ),
        parse_mode="HTML"
    )


# ответы на типы сообщений
@bot.message_handler(content_types=["sticker"])
def handle_sticker(message: types.Message):
    #bot.send_message(
    #    chat_id = message.chat.id, 
    #    text = "Классный стикер!", 
    #    reply_to_message_id = message.id
    #)
    bot.send_sticker(chat_id = message.chat.id, sticker = message.sticker.file_id)


@bot.message_handler(content_types = ["photo"], 
                     contains_word = "кот")
def handle_photo_with_cat_caption(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id, 
        text = "Какой классный кот!",
        reply_to_message_id = message.id
        )
    

@bot.message_handler(content_types=["photo"])
def handle_photo(message: types.Message):
    caption_text = "Классное фото! "
    if message.caption:
        caption_text += "Подпись:\n" + message.caption
    photo_file_id = message.photo[-1].file_id
    print(message.photo)
    for ph_size in message.photo:
        print(ph_size)
    bot.send_photo(
        chat_id = message.chat.id, 
        photo = photo_file_id,
        reply_to_message_id = message.id,
        caption = caption_text
        )
    #bot.send_message(
    #    chat_id = message.chat.id, 
    #    text = "Классное фото!",
    #    reply_to_message_id = message.id
    #)

@bot.message_handler(text = custom_filters.TextFilter(
        contains = ['погода'],
        ignore_case = True # перевод сообщения к нижнему регистру (когда регистр не важен)
        ))
def handle_weather_request(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = formatting.mbold("Хорошая погода!"),
        parse_mode = "MarkdownV2"
    )


@bot.message_handler(func = is_hi_in_message)
def handle_hi_message_text(message: types.Message):
    bot.send_message(
        chat_id = message.chat.id,
        text = "И тебе привет!"
    )

content_type_to_ru = {
    "text": "<текст>",
    "photo": "фото",                 
    "sticker": "стикер",
    "document": "документ"
    }

@bot.message_handler(is_reply = True)
def handle_reply_message(message: types.Message):
    message_type = message.reply_to_message.content_type
    if message_type in content_type_to_ru:
        message_type = content_type_to_ru[message_type]

    bot.send_message(
        chat_id = message.chat.id, 
        text = "Вы <b>ответили</b> на <u>сообщение</u>,"
        f"тип - {formatting.escape_html(message_type)}.",
        reply_to_message_id = message.reply_to_message.id,
        parse_mode = "HTML"
        )

@bot.message_handler(has_entities = True, contains_word = "проверка")
def copy_incoming_message(message: types.Message):
    named_entities = {entity.type for entity in message.entities}
    print(message.entities)
    text = formatting.format_text(
        message.text,
        f"Entities: {', '.join(named_entities)}",
        separator="\n\n"
    )
    bot.send_message(
        chat_id = message.chat.id,
        text = text,
        entities=message.entities,
    )

@bot.message_handler(contains_one_of_word = config.SAYONARA_CHECK)
def handle_goodbye_message(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.SAYONARA_MESSAGE,
        reply_to_message_id=message.id,
        parse_mode="HTML"
    )

@bot.message_handler()
def copy_incoming_message(message: types.Message):
    bot.copy_message(
        chat_id = message.chat.id,
        from_chat_id = message.chat.id,
        message_id = message.id,
    )



@bot.message_handler()
def send_echo_message(message: types.Message): 
    text = formatting.format_text(
        message.text,        
        message.entities,
    )

    bot.send_message(
        message.chat.id,
        text=text,
        entities=message.entities,
        parse_mode="HTML"
    )



# работа с инлайн режимом
# работа с числами

@bot.inline_handler(func=is_query_only_digits)
def inline_handler_handle_convert_inline_query(query: types.InlineQuery):
    handle_convert_inline_query(query, bot)

@bot.inline_handler(func=is_query_amount_and_available_currency)
def inline_handler_handle_convert_query_with_selected_currency(query: types.InlineQuery):
    handle_convert_query_with_selected_currency(query, bot)

@bot.inline_handler(func=is_query_amount_and_available_currencies_from_and_to)
def inline_handler_handle_convert_query_with_selected_currency_and_target_currency(query: types.InlineQuery):
    handle_convert_query_with_selected_currency_and_target_currency(query, bot)


@bot.inline_handler(func=is_query_only_digits)    
def inline_handler_handle_isdigit_inline_query(query: types.InlineQuery):
    handle_isdigit_inline_query(query, bot)

# любой другой запрос пойдет сюда

@bot.inline_handler(func=any_query)
def inline_handler_handle_any_inline_query(query: types.InlineQuery):
    handle_any_inline_query(query, bot)

if __name__ == "__main__":
    bot.enable_saving_states() # сохранить переменные в бинарном значении??
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.set_my_commands(default_commands)
    bot.infinity_polling(skip_pending = True, allowed_updates=[])

# line summary 712