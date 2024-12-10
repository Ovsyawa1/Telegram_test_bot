import requests
from decimal import Decimal
from telebot import util
from telebot import types
from functools import lru_cache
from datetime import date

JPY_RUB = 0.606

ERROR_FETCHING_VALUE = -1
ERROR_CURRENCY_NOT_FOUND = -2
ERROR_SECOND_CURRENCY_NOT_FOUND = -3

CURRENCIES_API_URL = (
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api"
    "@latest/v1/currencies/{currency}.json"
)

CURRENCIES_API_LIST_URL = (
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json"
)

FAVOURITE_CURRENCIES = [
    "RUB",
    "BYN",
    "JPY",
    "IDR"
]

DEFAULT_LOCAL_CURRENCY = "RUB"

default_currency_key = "default_currency"
local_currency_key = "local_currency"

def get_currencies_ratios(
    from_currency: str,
    to_currencies: list[str],
):
    from_currency = from_currency.lower()
    url = CURRENCIES_API_URL.format(currency=from_currency)
    response = requests.get(url)

    json_data = response.json(parse_float=Decimal)
    values = json_data[from_currency]

    result = []
    for currency in to_currencies:
        to_currency = currency.lower()
        if to_currency in values:
            result.append(values[to_currency])
        else:
            result.append(0)
    return result


def get_currency_ratios(from_currency: str, to_currencies: list[str]):
    from_currency = from_currency.lower()
    url = CURRENCIES_API_URL.format(currency=from_currency)
    response = requests.get(url)

    json_data = response.json(parse_float=Decimal)
    values = json_data[from_currency]
    
    result = []
    for currency in to_currencies:
        to_currency = currency.lower()
        if to_currency in values:
            result.append(values[to_currency])
        else:
            result.append(0)
    return result

def fetch_all_available_currencies():
    response = requests.get(CURRENCIES_API_LIST_URL)
    if response.status_code == 200:
        return response.json()
    return {}

@lru_cache(maxsize=1)
def fetch_available_currencies_for_date(the_date):

    print("Fetching available currencies for ", the_date)
    return fetch_all_available_currencies()

def get_latest_available_currencies():
    today = date.today().isoformat()
    return fetch_available_currencies_for_date()

def is_currency_available(currency: str) -> bool:
    return currency.lower() in fetch_all_available_currencies()

def get_currency_ratio(from_currency: str, to_currency: str):
    from_currency = from_currency.lower()
    to_currency = to_currency.lower()
    url = CURRENCIES_API_URL.format(currency=from_currency)
    response = requests.get(url)
    if response.status_code != 200:
        if response.status_code == 404:
            return ERROR_CURRENCY_NOT_FOUND
        return ERROR_FETCHING_VALUE
    
    json_data: dict = response.json(parse_float=Decimal)
    
    if to_currency not in json_data[from_currency]:
        return ERROR_SECOND_CURRENCY_NOT_FOUND

    return json_data[from_currency][to_currency]

def get_arguments_from_cvt_command(message: types.Message, default_to: str = "RUB"):
    arguments: str = util.extract_arguments(message.text)
    amount, _, list_of_currencies = arguments.partition(" ")
    list_of_currencies = list_of_currencies.split()

    if (len(list_of_currencies) > 2) or (len(list_of_currencies) == 0):
        return -1, -1, -1, -1
    elif (len(list_of_currencies) == 2):
        from_currency = list_of_currencies[0]
        to_currency = list_of_currencies[1]
    elif (len(list_of_currencies) == 1):
        from_currency = list_of_currencies[0]
        to_currency = default_to

    return (arguments, amount, from_currency, to_currency)


def get_jpy_to_rub_ratio():
    return get_currency_ratio(
        from_currency="JPY",
        to_currency="RUB",
    )