from secrets import token_urlsafe
from typing import Generator

from pcapi.core.offerers.models import OffererProvider
from pcapi.core.providers.models import Provider
from pcapi.models import db


def generate_hmac_key() -> str:
    return token_urlsafe(64)


def get_providers_with_no_hmac_key() -> Generator[Provider, None, None]:
    try:
        for provider in Provider.query.join(OffererProvider).filter(Provider.hmacKey.is_(None)).all():
            yield provider
    except Exception as err:
        print(f"Providers fetch failed: {err}")
        raise
    print("All providers fetched")


def run(dry_run: bool = True) -> None:
    message = "provider without hmac key"
    print(f"Starting {message} ...")
    for provider in get_providers_with_no_hmac_key():
        print(f"Updating provider {provider.id}, {provider.hmacKey}")
        provider.hmacKey = generate_hmac_key()
        print(f"updated provider {provider.id}, {provider.hmacKey}")

    if dry_run:
        db.session.rollback()
        print("Did rollback. Use dry_run = False if you want the script to commit.")
    else:
        db.session.commit()
        print("Did commit changes.")

    print(f"... {message} finished")
