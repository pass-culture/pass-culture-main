import os
import sys

import yaml

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

SECRET_KEYS: list[str] = []


def get(key: str, default: str | None = None) -> str:
    """
    Request a secret by it's key.

    This function add the key to the SECRET_KEYS list so that the secret will be requested and injected as an environnement variable.
    It's value is then extracted from environnement variables.

    Note that a secret is mandatory in all cloud environnement.

    A default value can still be provided, only for non deployed environnement (dev and test).
    If not specified, default is "" because string are enforced.
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
    secrets = sorted(set(SECRET_KEYS))
    yaml_content = {"secrets": [{"name": secret} for secret in secrets]}
    return yaml.dump(yaml_content)


@blueprint.cli.command("print_secret_keys")
def print_secret_keys() -> None:
    """
    Prints secret's keys list in yaml format.
    This output is used in deployment steps.
    """
    print(dump_secret_keys(), file=sys.stdout)
