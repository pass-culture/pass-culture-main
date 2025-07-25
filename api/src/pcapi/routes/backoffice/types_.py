import decimal
import typing


class StatsDataItems(typing.TypedDict):
    collective: decimal.Decimal
    individual: decimal.Decimal
    total: decimal.Decimal


class StatsData(typing.TypedDict):
    active: StatsDataItems
    inactive: StatsDataItems
    total_revenue: decimal.Decimal
    # TODO (igabriele, 2025-07-25): Is it used?
    placeholder: decimal.Decimal
