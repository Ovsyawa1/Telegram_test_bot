from telebot import formatting, types
from decimal import Decimal

HELP_MESSAGE = """Привет! Достапные команды:
- /start - начало работы с ботом
- /help - помощь (это сообщение)
- /joke - случайная шутка
- /jpy_to_rub 100 - конвертировать 100 JPY в RUB
- /cvt 100 JPY IDR - конвертировать 100 JPY в IDR (можно указать любые другие валюты, по умолчанию будет произведен перевод в RUB)
- /set_my_currency RUB - установить целевую валюту
- /set_local_currency BYN - установить локальную (исходную) валюту
"""
START_MESSAGE = "<b>Привет!</b> Давай Знакомиться!"

SET_LOCAL_CURRENCY_HELP_MESSAGE = formatting.format_text(
    "Успешно указать локальную валюту, например:",
    formatting.hcode("/set_local_currency RUB")
)

SET_LOCAL_CURRENCY_SUCCESS_MESSAGE = formatting.format_text(
    "Вы успешно указали локальную валюту"
)

#survey
SURVEY_CANCEL_SUGGESTION = formatting.format_text(
    "",
    formatting.format_text(
        "Отменить опрос можно командой /cancel или просто отправьте",
        formatting.hcode("отмена"),
        separator=" ",
    )
)
SURVEY_MESSAGE_WELCOME_FULL_NAME = formatting.format_text(
    "Добро пожаловать! Пожалуйста, представьтесь. ",
    "Напишите Ваше полное имя, например Иванов Иван.",
    SURVEY_CANCEL_SUGGESTION,
)
SURVEY_ERROR_MESSAGE_FULL_NAME = formatting.format_text(
    "Это не текст, а мы хотели бы узнать ваше имя",
    SURVEY_CANCEL_SUGGESTION,
)
SURVEY_MESSAGE_FULL_NAME_OK_AND_ASK_EMAIL = formatting.format_text(
    "Добро пожаловать, {full_name}! ",
    "Теперь укажите Вашу почту, пожалуйста"
)
SURVEY_ERROR_MESSAGE_EMAIL = formatting.format_text(
    "Это не настоящий email",
    "Пожалуйста введите Ваш email",
    SURVEY_CANCEL_SUGGESTION
)
SURVEY_MESSAGE_EMAIL_OK = formatting.format_text(
    "Спасибо за указанные данные",
    "Можно подписать Вас на рассылку?"
)
SURVEY_ERROR_MESSAGE_FAVOURITE_NUMBER = formatting.format_text(
    "Это не валидное число. Укажите настоящее число!",
    SURVEY_CANCEL_SUGGESTION
)
SURVEY_MESSAGE_INVALID_YES_OR_NO = formatting.format_text(
    "Не понимаю, укажите 'да' или 'нет'"
)
SURVEY_MESSAGE_CANCELLED = formatting.format_text(
    "Опрос отменен. Пройти заново: /survey"
)

RANDOM_MESSAGE_TEXT = formatting.format_text(
    "Вот сообщение с клавиатурой рандомом"
)

HELLO_MESSAGE = 'Привет! Как дела?'
HOW_ARE_YOU_MESSAGE = "У меня всё отлично! А у тебя?"
SAYONARA_MESSAGE = "<i>Надеюсь ещё увидимся~</i>"

SECRET_MESSAGE_FOR_ADMIN = "Секретка!"
SECRET_MESSAGE_NOT_ADMIN = "Нет секретки!" 

CVT_HELP_MESSAGE = "Пожалуйста, укажите аргумент конфертации, например:"
CONVERT_JPY_ERROR = formatting.format_text(
    CVT_HELP_MESSAGE,
    formatting.hcode("/jpy_to_rub 100"), #hcode
    separator=" "
)
IVALID_ARGUMENT_JPY_CONVERT = "Неправильный тип аргумента"
CVT_HOW_TO = formatting.format_text(
    CVT_HELP_MESSAGE,
    formatting.hcode("/cvt 100 JPY IDR"),
)
ERROR_FETCHING_CURRENCIES_TEXT = "Что-то пошло не так при запросе, попробуйте позже."
ERROR_NO_SUCH_CURRENCY = "Неизвестная валюта {currency}, введите существующую валюту"

SET_MY_CURRENCY_HELP_MESSAGE_TEXT = formatting.format_text("Пожалуйста, укажите выбранную валюту. Например: ",
                                                           formatting.hcode("/set_my_currency RUB"),
)               
SET_MY_CURRENCY_SUCCESS_MESSAGE_TEXT = formatting.format_text("Валюта по умолчанию успешно установлена:", "{currency}")

def format_currency_convert(
        from_currency: str, to_currency: str,
        from_amount, to_amount
        ):
    return formatting.format_text(
        formatting.hcode(f"{from_amount:,.2f}"),
        f"{from_currency.upper()} это примерно ",
        formatting.hcode(f"{to_amount:,.2f}"),
        f"{to_currency.upper()}",
        separator=" ",
    )

def format_jpy_to_rub_message(jpy_amount, rub_amount):
    return format_currency_convert(
        from_currency="JPY", to_currency="RUB",
        from_amount=jpy_amount, to_amount=rub_amount
    )

def format_message_content_currency_conversation(from_curr: str,  to_curr: str, amount_str, result_amount_str):
    
    content = types.InputTextMessageContent(
        message_text=formatting.format_text(
            f"{formatting.hcode(amount_str)} {from_curr} в {to_curr}" ,
            formatting.hcode(result_amount_str)
        ),
        parse_mode="HTML"
    )
    return content

def format_content_to_result_arcticle(from_currency: str, to_currency: str, amount, total_amount):
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    result_amount_str = f"{total_amount:,.2f}"
    amount_str = f"{amount:,}"
    content = format_message_content_currency_conversation(from_curr=from_curr, to_curr=to_curr, amount_str=amount_str, result_amount_str=result_amount_str)
    
    result = types.InlineQueryResultArticle(
        id=f"{from_currency}-{to_currency}-{amount}",
        title=f"{result_amount_str} {to_currency}",
        description=f"{amount_str} {from_curr} = {result_amount_str} {to_curr}",
        input_message_content=content,
    )
    
    return result

def prepare_default_resault_article(query_id):
    content = types.InputTextMessageContent(
        message_text=formatting.format_text(
            formatting.hbold("Это сообщение из inline запроса!"),
            f"id запроса inline: {formatting.hcode(query_id)}",
        ),
        parse_mode="HTML",
    )
    result = types.InlineQueryResultArticle(
        id="default-answer",
        title="Inline сообщение",
        description="Тут будет информация о текущем запросе и ответе",
        input_message_content=content,
    )
    return result

def format_message_content_currency_conversion(
    from_curr: str,
    to_curr: str,
    amount_str,
    result_amount_str,
):
    content = types.InputTextMessageContent(
        message_text=formatting.format_text(
            f"{formatting.hcode(amount_str)} {from_curr} в {to_curr}:",
            formatting.hcode(result_amount_str),
        ),
        parse_mode="HTML",
    )
    return content


def format_content_to_result_article(
    from_currency: str,
    to_currency: str,
    amount,
    total_amount,
):
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    amount_str = f"{amount:,}"
    result_amount_str = f"{total_amount:,.2f}"
    content = format_message_content_currency_conversion(
        from_curr=from_curr,
        to_curr=to_curr,
        amount_str=amount_str,
        result_amount_str=result_amount_str,
    )
    result = types.InlineQueryResultArticle(
        id=f"{from_currency}-{to_curr}-{amount}",
        title=f"{result_amount_str} {to_curr}",
        description=f"{amount_str} {from_curr} = {result_amount_str} {to_curr}",
        input_message_content=content,
    )
    return result


DONT_FORWARD_COMMANDS = "Пожалуйста, не пересылайте команды! Это может быть опасно!"

#r в начале строки отключает все спец символы \...
MARKDOWN_TEXT = r""" 
*bold \*text*
_italic \_text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=953652374)
![👍](tg://emoji?id=5368324170671202286)
`inline fixed-width code`
```
pre-formatted fixed-width code block
```
```python
pre-formatted fixed-width code block written in the Python programming language
```
>Block quotation started
>Block quotation continued
>Block quotation continued
>Block quotation continued
>The last line of the block quotation
**>The expandable block quotation started right after the previous block quotation
>It is separated from the previous block quotation by an empty bold entity
>Expandable block quotation continued
>Hidden by default part of the expandable block quotation started
>Expandable block quotation continued
>The last line of the expandable block quotation with the expandability mark||
"""

html_text = """
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=953652374">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
<blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>
<blockquote>Hehehe
</blockquote>
"""