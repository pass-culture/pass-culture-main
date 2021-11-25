import typing

from markupsafe import Markup


def yesno(value: typing.Any) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class="success" if value else "danger",
        text="Oui" if value else "Non",
    )
