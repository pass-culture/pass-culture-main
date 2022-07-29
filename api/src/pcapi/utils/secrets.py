import os
import sys

import yaml

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

SECRET_KEYS = []


@overload
def get(key: str, default: None = None) -> str | None:
    ...


@overload
def get(key: str, default: str) -> str:
    ...


def get(key: str, default: str | None = None) -> str | None:
    """
    Request a secret by it's key.

    This function add the key to the SECRET_KEYS list so that the secret will be requested and injected as an environnement variable.
    It's value is then extracted from environnement variables.

    Note that a secret is mandatory in all cloud environnement.

    A default value can still be provided, only for non deployed environnement (dev and test).
    The behavior of the default value is the same than os.environ.get
    """
    SECRET_KEYS.append(key)
    return os.environ.get(key, default)


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
