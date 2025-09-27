from pcapi.core.finance.utils import CurrencyEnum


MAX_STOCK_PRICE_IN_XPF = 23865
MAX_STOCK_PRICE_IN_EUR = 300

MAX_STOCK_PRICE_BY_CURRENCY = {
    CurrencyEnum.EUR: MAX_STOCK_PRICE_IN_EUR,
    CurrencyEnum.XPF: MAX_STOCK_PRICE_IN_XPF,
}

CURRENCY_NAME_MAPPING = {CurrencyEnum.EUR: "euros", CurrencyEnum.XPF: "francs Pacifique"}
