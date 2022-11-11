import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.routes.backoffice_v3 import offerers

from .helpers import unauthorized as unauthorized_helpers


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer):  # type: ignore
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture(scope="function", name="offer")
def offer_fixture(venue):  # type: ignore
    return offers_factories.OfferFactory(
        venue=venue,
        isActive=True,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )


@pytest.fixture(scope="function", name="booking")
def booking_fixture(offer):  # type: ignore
    stock = offers_factories.StockFactory(offer=offer)
    return bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.USED,
        quantity=1,
        amount=10,
        stock=stock,
    )


class GetOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_offerer(self, authenticated_client):  # type: ignore
        offerer = offerers_factories.UserOffererFactory().offerer
        url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get offerer (1 query)
        # get offerer basic info (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert offerer.name in content
        assert str(offerer.id) in content
        assert offerer.siren in content
        assert "Structure" in content


class GetOffererStatsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get_stats"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_stats(self, authenticated_client, offerer, offer, booking):  # type: ignore
        url = url_for("backoffice_v3_web.offerer.get_stats", offerer_id=offerer.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get total revenue (1 query)
        # get offerers offers stats (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        # cast to integer to avoid errors due to amount formatting
        assert str(int(booking.amount)) in content
        assert "1 IND" in content  # one active individual offer


class GetOffererStatsDataTest:
    def test_get_data(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        individual_offerer_bookings,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 4
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 5

        total_revenue = data.total_revenue

        assert total_revenue == 1694.0

    def test_individual_offers_only(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        individual_offerer_bookings,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 0
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 0

        total_revenue = data.total_revenue

        assert total_revenue == 30.0

    def test_collective_offers_only(
        self,
        offerer,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 4
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 5

        total_revenue = data.total_revenue

        assert total_revenue == 1664.0

    def test_no_bookings(self, offerer):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 0
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 0

        total_revenue = data.total_revenue

        assert total_revenue == 0.0


class GetOffererHistoryTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get_offerer_history"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_get_history(self, authenticated_client, offerer):
        action = history_factories.ActionHistoryFactory(offerer=offerer)
        url = url_for("backoffice_v3_web.offerer.get_offerer_history", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get offerer (1 query)
        # get history (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert action.comment in content
        assert action.authorUser.publicName in content

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_no_history(self, authenticated_client, offerer):
        url = url_for("backoffice_v3_web.offerer.get_offerer_history", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get offerer (1 query)
        # get history (1 query)
        with assert_num_queries(5):
            response = authenticated_client.get(url)
            assert response.status_code == 200


class GetOffererHistoryDataTest:
    def test_one_action(self):
        user_offerer = offerers_factories.UserOffererFactory()
        action = history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )

        offerer_id = user_offerer.offerer.id

        # get history (1 query)
        with assert_num_queries(1):
            history = offerers.get_offerer_history_data(offerer_id)

        assert len(history) == 1

        found_action = history[0]

        assert found_action.type == action.actionType.value
        assert found_action.date.astimezone() == action.actionDate.astimezone()
        assert found_action.authorName == action.authorUser.publicName

    def test_no_action(self, offerer):
        offerer_id = offerer.id

        # get history (1 query)
        with assert_num_queries(1):
            assert not offerers.get_offerer_history_data(offerer_id)

    def test_many_actions(self):
        user_offerer = offerers_factories.UserOffererFactory()
        actions = history_factories.ActionHistoryFactory.create_batch(
            3,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
        )

        offerer_id = user_offerer.offerer.id

        # get history (1 query)
        with assert_num_queries(1):
            history = offerers.get_offerer_history_data(offerer_id)

        assert len(history) == len(actions)

        found_comments = {event.comment for event in history}
        expected_comments = {event.comment for event in actions}

        assert found_comments == expected_comments


class NewCommentTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer_comment.new_comment"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_new_comment(self, authenticated_client, offerer):
        url = url_for("backoffice_v3_web.offerer_comment.new_comment", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get FF (1 query)
        # get offerer (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200


class CommentOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf, unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.offerer_comment.comment_offerer"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_add_comment(self, client, legit_user, offerer):
        comment = "some comment"
        response = self.send_comment_offerer_request(client, legit_user, offerer, comment)

        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id, _external=True)
        assert response.location == expected_url

        assert len(offerer.action_history) == 1
        assert offerer.action_history[0].comment == comment

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_add_invalid_comment(self, client, legit_user, offerer):
        response = self.send_comment_offerer_request(client, legit_user, offerer, "")

        assert response.status_code == 400
        assert not offerer.action_history

    def send_comment_offerer_request(self, client, legit_user, offerer, comment):
        authenticated_client = client.with_session_auth(legit_user.email)

        # generate and fetch (inside g) csrf token
        offerer_detail_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id)
        authenticated_client.get(offerer_detail_url)

        url = url_for("backoffice_v3_web.offerer_comment.comment_offerer", offerer_id=offerer.id)
        form = {"comment": comment, "csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)
