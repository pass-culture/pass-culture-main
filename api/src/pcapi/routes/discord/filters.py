import typing

from flask import Flask


def empty_string_if_null(data: typing.Any | None) -> str:
    if data is None:
        return ""
    return str(data)


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
