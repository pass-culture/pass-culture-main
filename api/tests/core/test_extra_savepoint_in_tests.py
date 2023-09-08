import pytest

import pcapi.core.users.factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
def test_show_extra_savepoint():
    # Ce test montre que pytest_flask_sqlalchemy envoie des
    # requêtes SAVEPOINT surnuméraires.
    user = users_factories.UserFactory(city="initial")

    try:
        user.city = "updated"
        # Excuté dans un test, cet appel à `flush()` envoie 2 requêtes SQL:
        # - UPDATE "user" SET city = ... WHERE id = ...
        # - SAVEPOINT
        # Ce SAVEPOINT n'est _PAS_ envoyé_ quand ce code est exécuté
        # hors des tests.
        db.session.flush()
        raise ValueError()
    except ValueError:
        # Exécuté dans un test, la ligne suivante rollback sur le
        # SAVEPOINT surnuméraire créé au-dessus (quand on appelle
        # `flush()`). Exécuté hors des tests, ce code ne créé pas ce
        # SAVEPOINT et ici on rollbacke donc sur un précédent BEGIN.
        db.session.rollback()
    # Parce qu'on rollback sur le SAVEPOINT surnuméraire, ce test
    # échoue car l'UPDATE n'a pas été rollbacké. Quand on exécuté le
    # même code hors de tests, par contre, cette assertion est vraie.
    assert user.city == "initial"


# Exécution dans un test:
#
#     SAVEPOINT sa_savepoint_1
#     INSERT INTO "user" ...
#     SAVEPOINT sa_savepoint_2
#     RELEASE SAVEPOINT sa_savepoint_2
#     SAVEPOINT sa_savepoint_3
#     SAVEPOINT sa_savepoint_4
#     SELECT ... FROM "user"
#     UPDATE "user" SET ...
#     SAVEPOINT sa_savepoint_5
#     ROLLBACK TO SAVEPOINT sa_savepoint_5
#     SAVEPOINT sa_savepoint_6
#     SELECT ... FROM "user"

# Exécution hors d'un test (dans un `flask shell`):
#
#     BEGIN (implicit)
#     INSERT INTO "user" ...
#     COMMIT
#     BEGIN (implicit)
#     SELECT ... FROM "user"
#     UPDATE "user" SET ...
#     ROLLBACK
#     BEGIN (implicit)
#     SELECT ... FROM "user"
