# Package `core`

Le code métier est segmenté entre différents sous-packages.

Chaque sous-package peut contenir les fichiers suivants :
- api.py : logiques métier et méthodes appelées par les points d'entrée de l'api (ex: les routes).
- commands.py : méthodes appelée via une commande flask
- models.py : définitions des entités
- repository.py : méthodes qui accèdent à la base de données
- validation.py : méthodes de validation des données


## Les fichiers `repository`

Ces modules contiennent des fonctions qui implémentent des _queries_ SQL Alchemy basées sur les _Models_
SQL Alchemy définis dans les fichiers `models.py`.

### Standards

Ces fonctions doivent contenir uniquement des requêtes vers la base de données qui retournent soit des tuples de données
"primitives" (e.g. une liste d'adresses email), soit des instances de modèles SQL Alchemy. On pourra aussi avoir des
fonctions qui retournent des "morceaux" de queries, c'est-à-dire des fonctions (privées) qui construisent des queries
qui ne sont pas déclenchées (i.e. qui n'ont pas de `.all()` ou `.first()`).
On utilisera des indications de type dans les signatures des fonctions pour indiquer quelles sont les données attendues
en entrée et en sortie.

Par exemple :

```python
def get_offerer_by_offer_id(offer_id: int) -> Offerer | None:
    return Offerer.query
        .join(Venue)
        .join(Offer)
        .filter_by(id=offer_id)
        .first()
```

Ces fonctions ne doivent pas contenir :

- Des notions relatives au `routing` (e.g. _status codes_ HTTP, verbes HTTP) ;
- Des règles de gestion ;
- Des appels à des web services.

### Tests

Pour que les données ne persistent pas en base de données après un test, la fixture `db_session`
est utilisée. Elle permet d'englober les requêtes à la base de données dans une transaction qui se rollback à la fin du test.

On doit parfois utiliser la fixture `clean_database` si on ne veut pas englober les requêtes dans une transaction.
La fixture se chargera de réinitialiser les données à la fin du test.

Cet exemple illustre un cas où l'on veut tester un `rollback` :

```python
import pytest

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db

from tests import conftest


@pytest.mark.usefixtures("db_session")
def test_flush_inside_transaction():
    venue_type = offerers_models.VenueType(label="Test")
    db.session.add(venue_type)
    db.session.flush()
    venue_type_id = venue_type.id
    db.session.rollback()
    assert offerers_models.VenueType.query.filter_by(id=venue_type_id).one() is not None # the object is still present


@conftest.clean_database
def test_flush_does_not_commit():
    venue_type = offerers_models.VenueType(label="Test")
    db.session.add(venue_type)
    db.session.flush()
    venue_type_id = venue_type.id
    db.session.rollback()
    assert offerers_models.VenueType.query.first() is None # the object is not anymore present
```


## Les fichiers `commands`

Ces fichiers contiennent des commandes que l'on peut appeler depuis l'extérieur. C'est le cas notamment des tâches récurrentes.

Par exemple la commande :
```python
@blueprint.cli.command("price_finance_events")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.PRICE_FINANCE_EVENTS)
def price_finance_events() -> None:
    finance_api.price_events()
```

peut être appelée en lançant : `flask price_finance_events` depuis le pod console.


Le décorateur `@log_cron_with_transaction` permet de logguer l'exécution des crons sous un format standard afin de profiter des outils de monitoring.

Le décorateur `@cron_require_feature` permet de vérifier que la fonctionnalité est activée avant l'exécution. Il doit être place le plus proche de la signature de la fonction.
