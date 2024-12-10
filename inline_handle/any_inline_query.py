import messages


from telebot import types, TeleBot


def handle_any_inline_query(query: types.InlineQuery, bot: TeleBot):
    result = messages.prepare_default_resault_article(str(query.id))
    results = [result]
    bot.answer_inline_query(
        inline_query_id=query.id,
        results=results,
        cache_time=10,
    )