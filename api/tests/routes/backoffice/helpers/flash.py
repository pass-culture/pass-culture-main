from flask import url_for

from .html_parser import extract_htmx_flash


def get_htmx_flash_messages(client) -> dict[str, set[str]]:
    response = client.get(url_for("backoffice_web.get_messages"))
    assert response.status_code == 200
    return extract_htmx_flash(response.data)
