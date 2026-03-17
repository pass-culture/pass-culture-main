import typing

from pcapi.core.finance.utils import CurrencyEnum


MAX_OFFER_NAME_LENGTH: typing.Final = 90

OFFERS_RECAP_LIMIT: typing.Final = 101
OFFERS_HOMEPAGE_LIMIT: typing.Final = 3


MAX_STOCK_PRICE_IN_XPF: typing.Final = 23865
MAX_STOCK_PRICE_IN_EUR: typing.Final = 300

MAX_STOCK_PRICE_BY_CURRENCY: typing.Final = {
    CurrencyEnum.EUR: MAX_STOCK_PRICE_IN_EUR,
    CurrencyEnum.XPF: MAX_STOCK_PRICE_IN_XPF,
}

CURRENCY_NAME_MAPPING: typing.Final = {
    CurrencyEnum.EUR: "euros",
    CurrencyEnum.XPF: "francs Pacifique",
}
