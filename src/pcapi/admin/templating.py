import typing

from markupsafe import Markup


def yesno(value: typing.Any) -> str:
    css_class = "success" if value else "danger"
    text_value = "Oui" if value else "Non"
    return Markup(f"""<span class="badge badge-{css_class}">{text_value}</span>""")
