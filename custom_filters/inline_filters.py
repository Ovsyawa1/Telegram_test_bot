import currencies
import messages


from telebot import types, TeleBot


def handle_any_convert_to_many_inline_query(
    bot: TeleBot,
    query: types.InlineQuery,
    amount: int,
    from_currency: str,
    target_currencies: list[str],
):
    ratios = currencies.get_currencies_ratios(
        from_currency=from_currency,
        to_currencies=target_currencies,
    )

    results = []

    for currency_rate, currency_name in zip(
        ratios,
        target_currencies,
    ):
        total_amount = amount * currency_rate
        result = messages.format_content_to_result_article(
            from_currency=from_currency,
            to_currency=currency_name,
            amount=amount,
            total_amount=total_amount,
        )
        results.append(result)

    bot.answer_inline_query(
        inline_query_id=query.id,
        results=results,
        cache_time=10,
    )


def is_query_only_digits(query: types.InlineQuery):
    if query and query.query:
        return query.query.isdigit()
    return False


def is_query_amount_and_available_currency(query: types.InlineQuery):
    text = query.query or ""
    amount, _, currency = text.partition(" ")
    if not amount.isdigit():
        return False

    return currencies.is_currency_available(currency)


def is_query_amount_and_available_currencies_from_and_to(query: types.InlineQuery):
    text = query.query or ""
    amount, _, currencies_from_and_to = text.partition(" ")
    if not amount.isdigit():
        return False

    from_currency, _, to_currency = currencies_from_and_to.partition(" ")
    if not amount.isdigit():
        return False

    from_currency, _, to_currency = currencies_from_and_to.partition(" ")
    if not currencies.is_currency_available(from_currency):
        return False
    if not currencies.is_currency_available(to_currency):
        return False
    return True


def any_query(query: types.InlineQuery):
    print(query)
    return True