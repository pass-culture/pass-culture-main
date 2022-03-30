import itertools
import types

import pytest

import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.utils.db as db_utils


@pytest.mark.usefixtures("db_session")
class GetBatchesTest:
    def test_basics(self):
        users = users_factories.UserFactory.create_batch(11)
        batches = db_utils.get_batches(users_models.User.query, users_models.User.id, 2)
        assert isinstance(batches, types.GeneratorType)
        batches = list(batches)
        assert len(batches) == 6
        assert list(batches[0].order_by(users_models.User.id)) == [users[0], users[1]]
        assert list(batches[1].order_by(users_models.User.id)) == [users[2], users[3]]
        assert list(batches[2].order_by(users_models.User.id)) == [users[4], users[5]]
        assert list(batches[3].order_by(users_models.User.id)) == [users[6], users[7]]
        assert list(batches[4].order_by(users_models.User.id)) == [users[8], users[9]]
        assert list(batches[5].order_by(users_models.User.id)) == [users[10]]
        assert sorted(list(itertools.chain.from_iterable(batches)), key=lambda x: x.id) == users

    def test_empty(self):
        batches = db_utils.get_batches(users_models.User.query, users_models.User.id, 10)
        assert not list(batches)
