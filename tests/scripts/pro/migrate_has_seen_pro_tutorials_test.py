from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.scripts.pro.migrate_has_seen_pro_tutorials import migrate_has_seen_pro_tutorials


@pytest.mark.usefixtures("db_session")
def should_udpate_has_seen_pro_tutorials_by_batch():
    today = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)
    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=yesterday)
    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=yesterday)
    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=yesterday)
    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=yesterday)
    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=yesterday)

    users_factories.ProFactory(hasSeenProTutorials=False, dateCreated=today)
    users_factories.BeneficiaryFactory(hasSeenProTutorials=False, dateCreated=yesterday)

    migrate_has_seen_pro_tutorials(1)

    saved_users = User.query.order_by(User.id).all()
    assert saved_users[0].hasSeenProTutorials == True
    assert saved_users[1].hasSeenProTutorials == True
    assert saved_users[2].hasSeenProTutorials == True
    assert saved_users[3].hasSeenProTutorials == True
    assert saved_users[4].hasSeenProTutorials == True
    assert saved_users[5].hasSeenProTutorials == False
    assert saved_users[6].hasSeenProTutorials == False
