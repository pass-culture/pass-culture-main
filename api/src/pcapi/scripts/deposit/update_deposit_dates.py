"""
Le 13 avril vers 9h40, un script a été éxécuté pour mettre à jour les dates d'expiration des deposit.
Dans ce script, il y avait une erreur :
On regardait si la date contenait 0 pour les heures et les minutes, auquel cas on les transformait en 23 et 59.
Pour les dates d'expiration qui étaient déjà au jour d'après, ça a repoussé le délai d'expiration de 23h59 :
2021-31-05 10:49 sur la date d'OBTENTION donnait 2023-06-01 00:00 sur la date d'EXPIRATION et est passé à 2023-06-01 23:59.

Ces heures étant UTC, sur le front actuellement (2023-05-23), un `new Date(expirationDate)` donne 2023-06-02 01:59,
ce qui conduit à l'affichage 02/06/2023.

De plus, pour une raison inconnue, l'éxécution du script a été apparemment interrompue à la moitié, laissant en base
des dates d'expiration à 00:00 du jour suivant et d'autres à 23:59 du jour suivant.

De plus un correctif avait été fait pour enregistrer la date d'expiration selon l'heure de Paris.

Le but de ce script ici est de toutes les passer à 23:59:59.999999 la jour d'après, pour un cohérence totale pour le front.
"""

import datetime
from functools import wraps
import logging
import time

from dateutil.relativedelta import relativedelta

from pcapi.core.finance.models import Deposit
from pcapi.models import db


logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.DEBUG)


def timed(func):  # type: ignore[no-untyped-def]
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("%s ran in %ss", func.__name__, round(end - start, 2))
        return result

    return wrapper


@timed
def update_deposit_expiration_dates(dry_run: bool = True, batch_size: int = 1000) -> None:
    query = Deposit.query.filter(
        Deposit.expirationDate > datetime.datetime.utcnow(),
        Deposit.type == "GRANT_18",
    )
    total = query.count()
    print(f"Found {total} deposits to update")

    count = 0
    start_index = 0

    while start_index < total:
        deposits_to_update = query.offset(start_index).limit(batch_size).all()
        for deposit in deposits_to_update:
            date_created = deposit.dateCreated.date()
            # old_expiration_date = deposit.expirationDate
            new_expiration_date = date_created + relativedelta(years=2, days=1)
            deposit.expirationDate = datetime.datetime.combine(new_expiration_date, datetime.time.max)
            # print(f"Updating deposit {deposit.id} from {old_expiration_date} to {new_expiration_datetime}")
            count += 1

        start_index += batch_size
        if dry_run:
            print(f"Dry run. Would have updated {count} deposits out of {total} ({count / total * 100:.2f}%)")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"Updated {count} deposits out of {total} ({count / total * 100:.2f}%)")

    print("Done")
