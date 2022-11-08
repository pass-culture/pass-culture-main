import datetime
import typing

from flask import Flask

from pcapi.core.users import models as users_models


def format_state(is_active: bool) -> str:
    if is_active:
        return "Actif"
    return "Suspendu"


def format_role(role: str | None) -> str:
    if not role:
        return "Aucune information"

    match role:
        case users_models.UserRole.ADMIN:
            return "Admin"
        case users_models.UserRole.PRO:
            return "Pro"
        case users_models.UserRole.TEST:
            return "Test"
        case users_models.UserRole.BENEFICIARY:
            return "Pass 18"
        case users_models.UserRole.UNDERAGE_BENEFICIARY:
            return "Pass 15-17"
        case _:
            return "Aucune information"


def format_phone_number(phone_number: str) -> str:
    if not phone_number:
        return ""

    return phone_number


def empty_string_if_null(data: typing.Any | None) -> str:
    if data is None:
        return ""
    return str(data)


def format_date(data: datetime.date | datetime.datetime, strformat: str = "%d/%m/%Y") -> str:
    if not data:
        return ""
    return data.strftime(strformat)


def format_amount(amount: float) -> str:
    return f"{amount:,.2f} €".replace(",", "&#8239;").replace(".", ",")


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["format_state"] = format_state
    app.jinja_env.filters["format_role"] = format_role
    app.jinja_env.filters["format_phone_number"] = format_phone_number
    app.jinja_env.filters["format_amount"] = format_amount
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
    app.jinja_env.filters["format_date"] = format_date
