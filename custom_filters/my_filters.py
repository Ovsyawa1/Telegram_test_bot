from telebot import types, util
from telebot.types import Message
import config
from telebot.custom_filters import(
    SimpleCustomFilter,
    AdvancedCustomFilter
)

class IsUserAdminOfBot(SimpleCustomFilter):
    key = "is_bot_admin"

    def check(self, message: Message):
        return message.from_user.id in config.ADMIN_LIST
    
class HasEntitiesFilter(SimpleCustomFilter):
    key = "has_entities"

    def check(self, message: Message) -> bool:
        return bool(message.entities)

class ContainsWordFilter(AdvancedCustomFilter):
    key = "contains_word"

    def check(self, message: Message, word: str) -> bool:
        text = message.text or message.caption
        if not text: # если оба варианта окажутся None, тогда верни False
            return False
        
        return word in text.lower()
    
class ContainsOneOfWordFilter(AdvancedCustomFilter):
    key = "contains_one_of_word"

    def check(self, message: Message, words: list[str]) -> bool:
        text = message.text or message.caption
        if not text: # если оба варианта окажутся None, тогда верни False
            return False
        
        return any(word.lower() in text.lower() for word in words)


def current_chat_is_not_user_chat(message: types.Message):
    return message.chat.id != message.from_user.id


def is_hi_in_message(message: types.Message):
    return message.text and "привет" in message.text.lower()


def is_cat_caption(message: types.Message):
    return message.caption and "кот" in message.caption.lower() # сначала проверяем существует ли подпись, так как у None нет метода lower


def has_no_command_arguments(message: types.Message):
    return not util.extract_arguments(message.text)