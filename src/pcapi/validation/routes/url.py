from pcapi.models import ApiErrors


def is_url_safe(url: str):
    if url and not _has_proper_prefix(url):
        errors = ApiErrors()
        errors.add_error("url", 'L\'URL doit commencer par "http://" ou "https://"')
        raise errors


def _has_proper_prefix(url):
    return url.startswith("http://") or url.startswith("https://")
