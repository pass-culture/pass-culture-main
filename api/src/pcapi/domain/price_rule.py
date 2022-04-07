import enum
from functools import partial


class AllocineStocksPriceRule(Exception):
    pass


def default_price(*args):  # type: ignore [no-untyped-def]
    return True


class PriceRule(enum.Enum):
    default = partial(default_price)

    def __call__(self, *args):  # type: ignore [no-untyped-def]
        return self.value(*args)
