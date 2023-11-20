from werkzeug.exceptions import NotFound

from .allocine import AllocineContext
from .base import PivotContext
from .boost import BoostContext
from .cgr import CGRContext
from .cineoffice import CineofficeContext
from .ems import EMSContext


def get_context(provider_name: str) -> type[PivotContext]:
    context = {
        "allocine": AllocineContext,
        "boost": BoostContext,
        "cgr": CGRContext,
        "cineoffice": CineofficeContext,
        "ems": EMSContext,
    }.get(provider_name)

    if not context:
        raise NotFound()

    return context
