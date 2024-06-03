import os
import sys

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

SECRET_KEYS: list[str] = []


def get(key: str, default: str | None = None) -> str:
    """
    Request a secret by its key.

    This function adds the key to the SECRET_KEYS list so that the secret will be requested and injected as an environment variable.
    Its value is then extracted from environment variables.

    Note that a secret is mandatory in all cloud environments.

    A default value can still be provided, only for non deployed environments (dev and test).
    If not specified, default is "" because strings are enforced.
    """
    SECRET_KEYS.append(key)
    return os.environ.get(key, default or "").strip()


def getlist(key: str, separator: str = ",", type_: type = str) -> list:
    """Return a secret as a (possibly empty) list.

    See ``get`` for further details.
    """
    separated_values = get(key)
    if not separated_values:
        return []
    return [type_(v) for v in separated_values.split(separator)]


def dump_secret_keys() -> str:
    out = ["secrets:"]
    for secret in sorted(set(SECRET_KEYS)):
        out.append(f"- name: {secret}")
    out.append("")  # final newline
    return "\n".join(out)


def _check_secret_list_has_been_initialized() -> None:
    if not SECRET_KEYS:
        raise ValueError("The list of secrets has not been initialized.")


@blueprint.cli.command("print_secret_keys")
def print_secret_keys() -> None:
    """
    Prints secret's keys list in yaml format.
    This output is used in deployment steps.
    """
    _check_secret_list_has_been_initialized()

    print(dump_secret_keys())


@blueprint.cli.command("check_secrets")
def check_secrets() -> None:
    """Make sure that all secrets are defined and non-empty."""
    _check_secret_list_has_been_initialized()

    missing = set()
    for secret in SECRET_KEYS:
        if not os.environ.get(secret):
            missing.add(secret)

    if missing:
        sys.exit(f"The following secrets are missing: {', '.join(sorted(missing))}")
