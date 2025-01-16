from decimal import Decimal

from pcapi.core.finance.utils import euros_to_xpf
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models


def format_price(
    amount_in_euros: int | float | Decimal,
    target: users_models.User | offerers_models.Offerer | offerers_models.Venue | None,
) -> str:
    # format for transactional emails
    if not amount_in_euros:
        return "Gratuit"

    if target and target.is_caledonian:
        amount_in_xpf = euros_to_xpf(amount_in_euros)
        return f"{amount_in_xpf} F"

    places = 0 if Decimal(amount_in_euros) % 1 == 0 else 2
    return f"{amount_in_euros:.{places}f} €".replace(".", ",")
