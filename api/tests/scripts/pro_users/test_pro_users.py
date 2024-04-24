import datetime

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.scripts.pro_user.set_eligibility.make_user_eligible import make_users_eligible_orm


class UserProTest:
    @pytest.mark.usefixtures("db_session")
    def test_set_eligibilityDate(self, db_session):
        ids = [1, 2, 3, 5, 6, 7, 4]
        for _ in ids:
            user = users_factories.ProFactory()
            db_session.add(user)
        make_users_eligible_orm(ids=ids, date_eligible=datetime.datetime.utcnow(), phase=1)
        users = users_models.User.query.all()
        assert len(users) == len(ids)

    @pytest.mark.usefixtures("db_session")
    def test_update_eligibility_date(self, db_session):
        ids = [1, 2, 3, 5, 6, 7, 4]
        date_n = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        users_factories.UserProNewNavStateFactory(eligibilityDate=date_n)
        users_factories.UserProNewNavStateFactory(eligibilityDate=date_n)

        for _ in ids[2:]:
            user = users_factories.ProFactory()
            db_session.add(user)

        make_users_eligible_orm(ids=ids, date_eligible=datetime.datetime.utcnow(), phase=1)
        users = users_models.User.query.all()
        assert len(users) == len(ids)
        updated_states = users_models.UserProNewNavState.query.filter(
            users_models.UserProNewNavState.userId.in_([1, 2])
        ).all()
        for state in updated_states:
            assert state.eligibilityDate != date_n
