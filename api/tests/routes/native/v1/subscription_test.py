import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_next_subscription_test(client):
    user = users_factories.UserFactory(
        dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        - relativedelta(years=18, months=5),
    )

    client.with_token(user.email)

    response = client.get("/native/v1/subscription/next_step")

    assert response.status_code == 200
    assert response.json == {"nextSubscriptionStep": "phone-validation"}
