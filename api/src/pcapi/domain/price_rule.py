import enum
from functools import partial


class AllocineStocksPriceRule(Exception):
    pass


def default_price(*args):
    return True


class PriceRule(enum.Enum):
    default = partial(default_price)

    def __call__(self, *args):
        return self.value(*args)
