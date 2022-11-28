import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import tag_categories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice_v3 import offerers

from .helpers import html_parser
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
        assert found_action.date == action.actionDate
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


class ListOfferersToValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.validate_offerer.list_offerers_to_validate"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ListOfferersToValidateTest:
    class ListOfferersToBeValidatedTest:
        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_offerers_to_be_validated(self, authenticated_client):
            # given
            _validated_offerers = [offerers_factories.UserOffererFactory().offerer for _ in range(3)]
            to_be_validated_offerers = []
            for _ in range(4):
                user_offerer = offerers_factories.UserNotValidatedOffererFactory()
                history_factories.ActionHistoryFactory(
                    actionType=history_models.ActionType.OFFERER_NEW,
                    authorUser=users_factories.AdminFactory(),
                    offerer=user_offerer.offerer,
                    user=user_offerer.user,
                    comment=None,
                )
                to_be_validated_offerers.append(user_offerer.offerer)

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert sorted([int(row["ID"]) for row in rows]) == sorted(o.id for o in to_be_validated_offerers)

        @pytest.mark.parametrize(
            "validation_status,expected_status",
            [
                (None, "Nouvelle"),
                (offerers_models.ValidationStatus.NEW, "Nouvelle"),
                (offerers_models.ValidationStatus.PENDING, "En attente"),
            ],
        )
        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_payload_content(self, authenticated_client, validation_status, expected_status):
            # given
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
                offerer__validationStatus=validation_status,
                user__phoneNumber="+33610203040",
            )
            commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 12, 0),
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                user=user_offerer.user,
                comment=None,
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 13, 1),
                actionType=history_models.ActionType.COMMENT,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                comment="Bla blabla",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 14, 2),
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                comment="Houlala",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 15, 3),
                actionType=history_models.ActionType.USER_OFFERER_VALIDATED,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                user=user_offerer.user,
                comment=None,
            )
            offerers_factories.OffererTagFactory(
                name="top-acteur", label="Top Actor", categoryId=tag_categories.HOMOLOGATION.id
            )

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name.upper()
            assert rows[0]["État"] == expected_status
            assert rows[0]["Top Acteur"] == ""  # no text
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == "Houlala"
            assert rows[0]["SIREN"] == user_offerer.offerer.siren
            assert rows[0]["Email"] == user_offerer.offerer.UserOfferers[0].user.email
            assert (
                rows[0]["Responsable Structure"] == f"{user_offerer.offerer.UserOfferers[0].user.firstName} "
                f"{user_offerer.offerer.UserOfferers[0].user.lastName}"
            )
            assert rows[0]["Ville"] == user_offerer.offerer.city
            assert rows[0]["Téléphone"] == user_offerer.offerer.UserOfferers[0].user.phoneNumber

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_payload_content_no_action(self, authenticated_client):
            # given
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
            )

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name.upper()
            assert rows[0]["État"] == "Nouvelle"
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == ""

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        @pytest.mark.parametrize(
            "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
            (
                (31, {"per_page": 10}, 4, 1, 10),
                (31, {"per_page": 10, "page": 1}, 4, 1, 10),
                (31, {"per_page": 10, "page": 3}, 4, 3, 10),
                (31, {"per_page": 10, "page": 4}, 4, 4, 1),
                (20, {"per_page": 10, "page": 1}, 2, 1, 10),
                (27, {"page": 1}, 1, 1, 27),
                (10, {"per_page": 25, "page": 1}, 1, 1, 10),
            ),
        )
        def test_list_pagination(
            self,
            authenticated_client,
            total_items,
            pagination_config,
            expected_total_pages,
            expected_page,
            expected_items,
        ):
            # given
            for _ in range(total_items):
                offerers_factories.UserNotValidatedOffererFactory()

            # when
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", **pagination_config)
            )

            # then
            assert response.status_code == 200
            assert html_parser.count_table_rows(response.data) == expected_items
            assert html_parser.extract_pagination_info(response.data) == (
                expected_page,
                expected_total_pages,
                total_items,
            )

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        @pytest.mark.parametrize(
            "tag_filter, expected_offerer_names",
            (
                (["Top acteur"], {"B", "E", "F"}),
                (["Collectivité"], {"C", "E"}),
                (["Établissement public"], {"D", "F"}),
                (["Établissement public", "Top acteur"], {"F"}),
            ),
        )
        def test_list_filtering_by_tags(
            self, authenticated_client, tag_filter, expected_offerer_names, offerers_to_be_validated
        ):
            # given
            tags = (
                offerers_models.OffererTag.query.filter(offerers_models.OffererTag.label.in_(tag_filter))
                .with_entities(offerers_models.OffererTag.id)
                .all()
            )
            tags_ids = [_id for _id, in tags]

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", tags=tags_ids)
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == expected_offerer_names

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_filtering_by_date(self, authenticated_client):
            # given
            # Created before requested range, excluded from results:
            user_offerer_2 = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 4, 4)
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 11, 4, 4),
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=user_offerer_2.user,
                offerer=user_offerer_2.offerer,
                user=user_offerer_2.user,
            )
            # Created within requested range:
            user_offerer_3 = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 6, 5)
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 11, 6, 5),
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=user_offerer_3.user,
                offerer=user_offerer_3.offerer,
                user=user_offerer_3.user,
            )
            # No history, in requested range:
            user_offerer_4 = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 8, 6)
            )
            # No history, excluded from results:
            offerers_factories.UserNotValidatedOffererFactory(offerer__dateCreated=datetime.datetime(2022, 11, 10, 7))

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for(
                        "backoffice_v3_web.validate_offerer.list_offerers_to_validate",
                        from_date="2022-11-05",
                        to_date="2022-11-08",
                    )
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            ids = [int(row["ID"]) for row in rows]
            assert sorted(ids) == sorted(uo.offerer.id for uo in (user_offerer_3, user_offerer_4))

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_filtering_by_invalid_date(self, authenticated_client):
            # given

            # when
            response = authenticated_client.get(
                url_for(
                    "backoffice_v3_web.validate_offerer.list_offerers_to_validate",
                    from_date="05/11/2022",
                )
            )

            # then
            assert response.status_code == 400
            assert "Date invalide" in response.data.decode("utf-8")

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_search_by_siren(self, authenticated_client, offerers_to_be_validated):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", q="123004004")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"D"}

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        @pytest.mark.parametrize("siren", ["12345678", "1234567890"])
        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_search_by_invalid_siren(self, authenticated_client, siren):
            # when
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", q=siren)
            )

            # then
            assert response.status_code == 400
            assert "Le SIREN doit faire 9 caractères" in response.data.decode("utf-8")

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        @pytest.mark.parametrize(
            "search_filter, expected_offerer_names",
            (
                ("cinema de la plage", {"Cinéma de la Petite Plage", "Cinéma de la Grande Plage"}),
                ("cinéma", {"Cinéma de la Petite Plage", "Cinéma de la Grande Plage", "Cinéma du Centre"}),
                ("Plage", {"Librairie de la Plage", "Cinéma de la Petite Plage", "Cinéma de la Grande Plage"}),
                ("Librairie du Centre", set()),
            ),
        )
        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_list_search_by_name(self, authenticated_client, search_filter, expected_offerer_names):
            # given
            for name in (
                "Librairie de la Plage",
                "Cinéma de la Petite Plage",
                "Cinéma du Centre",
                "Cinéma de la Grande Plage",
            ):
                offerers_factories.NotValidatedOffererFactory(name=name)

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", q=search_filter)
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {name.upper() for name in expected_offerer_names}

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        @pytest.mark.parametrize(
            "status_filter, expected_status, expected_offerer_names",
            (
                ("NEW", 200, {"A", "C", "E"}),
                ("PENDING", 200, {"B", "D", "F"}),
                (["NEW", "PENDING"], 200, {"A", "B", "C", "D", "E", "F"}),
                ("VALIDATED", 200, {"G"}),
                ("REJECTED", 200, {"H"}),
                (None, 200, {"A", "B", "C", "D", "E", "F"}),  # same as default
                ("OTHER", 400, set()),  # unknown value
                (["REJECTED", "OTHER"], 400, set()),
            ),
        )
        def test_list_filtering_by_status(
            self, authenticated_client, status_filter, expected_status, expected_offerer_names, offerers_to_be_validated
        ):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate", status=status_filter)
                )

            # then
            assert response.status_code == expected_status
            if expected_status == 200:
                rows = html_parser.extract_table_rows(response.data)
                assert {row["Nom de la structure"] for row in rows} == expected_offerer_names
            else:
                assert html_parser.count_table_rows(response.data) == 0

        @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
        def test_offerers_stats_are_displayed(self, authenticated_client, offerers_to_be_validated):
            # when
            response = authenticated_client.get(url_for("backoffice_v3_web.validate_offerer.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            cards = html_parser.extract_cards_text(response.data)
            assert "3 nouvelles structures" in cards
            assert "3 structures en attente" in cards
            assert "1 structure validée" in cards
            assert "1 structure rejetée" in cards


class ValidateOffererUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.offerer.validate"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ValidateOffererTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_validate_offerer(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.validate", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_validate_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # given

        # when
        response = authenticated_client.post(url_for("backoffice_v3_web.offerer.validate", offerer_id=1))

        # then
        assert response.status_code == 404

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_cannot_validate_offerer_already_validated(self, authenticated_client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.validate", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 400

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà validée" in redirected_response.data.decode("utf8")


class RejectOffererUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.offerer.reject"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class RejectOffererTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_reject_offerer(self, legit_user, authenticated_client):
        # given
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected

        # when
        response = authenticated_client.post(url_for("backoffice_v3_web.offerer.reject", offerer_id=offerer.id))

        # then
        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.isRejected
        assert not user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_reject_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # given

        # when
        response = authenticated_client.post(url_for("backoffice_v3_web.offerer.reject", offerer_id=1))

        # then
        assert response.status_code == 404

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_cannot_reject_offerer_already_rejected(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(validationStatus=offerers_models.ValidationStatus.REJECTED)

        # when
        response = authenticated_client.post(url_for("backoffice_v3_web.offerer.reject", offerer_id=offerer.id))

        # then
        assert response.status_code == 400

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà rejetée" in redirected_response.data.decode("utf8")


class SetOffererPendingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.offerer.set_pending"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class SetOffererPendingTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_set_offerer_pending(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.set_pending", offerer_id=offerer.id),
            form={"comment": "En attente de documents"},
        )

        # then
        assert response.status_code == 303

        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.validationStatus == offerers_models.ValidationStatus.PENDING
        action = history_models.ActionHistory.query.one()

        assert action.actionType == history_models.ActionType.OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_set_offerer_pending_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # given

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.set_pending", offerer_id=1),
            form={"comment": "Questionnaire"},
        )
        # then
        assert response.status_code == 404


class ToggleTopActorUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.offerer.toggle_top_actor"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ToggleTopActorTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_toggle_is_top_actor(self, authenticated_client):
        # given
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer
        tag = offerers_factories.OffererTagFactory(
            name="top-acteur", label="Top acteur", categoryId=tag_categories.HOMOLOGATION.id
        )

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.toggle_top_actor", offerer_id=offerer.id), form={"is_top_actor": "on"}
        )

        # then
        assert response.status_code == 303
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == tag.id
        assert offerer_mappings[0].offererId == offerer.id

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.toggle_top_actor", offerer_id=offerer.id), form={}
        )

        # then
        assert response.status_code == 303
        assert offerers_models.OffererTagMapping.query.count() == 0

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_toggle_is_top_actor_twice_true(self, authenticated_client):
        # given
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer
        tag = offerers_factories.OffererTagFactory(
            name="top-acteur", label="Top acteur", categoryId=tag_categories.HOMOLOGATION.id
        )

        # when
        for _ in range(2):
            response = authenticated_client.post(
                url_for("backoffice_v3_web.offerer.toggle_top_actor", offerer_id=offerer.id),
                form={"is_top_actor": "on"},
            )

            # then
            assert response.status_code == 303

        # then
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == tag.id
        assert offerer_mappings[0].offererId == offerer.id

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_toggle_top_actor_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # given

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.offerer.toggle_top_actor", offerer_id=1), form={"is_top_actor": "on"}
        )
        # then
        assert response.status_code == 404


class ListUserOffererToValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ListUserOffererToValidateTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_list_only_user_offerer_to_be_validated(self, authenticated_client):
        # given
        to_be_validated = []
        for _ in range(2):
            validated_user_offerer = offerers_factories.UserOffererFactory()
            new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(offerer=validated_user_offerer.offerer)
            to_be_validated.append(new_user_offerer)
            pending_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
                offerer=validated_user_offerer.offerer, validationStatus=offerers_models.ValidationStatus.PENDING
            )
            to_be_validated.append(pending_user_offerer)
            for action_type in (
                history_models.ActionType.USER_OFFERER_PENDING,
                history_models.ActionType.USER_OFFERER_PENDING,
            ):
                history_factories.ActionHistoryFactory(
                    actionType=action_type,
                    authorUser=users_factories.AdminFactory(),
                    offerer=pending_user_offerer.offerer,
                    user=pending_user_offerer.user,
                    comment=None,
                )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {int(row["ID Compte pro"]) for row in rows} == {user_offerer.user.id for user_offerer in to_be_validated}

    @pytest.mark.parametrize(
        "validation_status,expected_status",
        [
            (offerers_models.ValidationStatus.NEW, "Nouveau"),
            (offerers_models.ValidationStatus.PENDING, "En attente"),
        ],
    )
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_payload_content(self, authenticated_client, validation_status, expected_status):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 2, 11, 30),
            dateCreated=datetime.datetime(2022, 11, 2, 11, 59),
        )
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer,
            validationStatus=validation_status,
            dateCreated=datetime.datetime(2022, 11, 3, 11, 59),
            user__phoneNumber="+33612345678",
        )
        commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 3, 12, 0),
            actionType=history_models.ActionType.USER_OFFERER_NEW,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 4, 13, 1),
            actionType=history_models.ActionType.COMMENT,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment="Bla blabla" if validation_status == offerers_models.ValidationStatus.NEW else "Premier",
        )
        if validation_status == offerers_models.ValidationStatus.PENDING:
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 11, 5, 14, 2),
                actionType=history_models.ActionType.USER_OFFERER_PENDING,
                authorUser=commenter,
                offerer=new_user_offerer.offerer,
                user=new_user_offerer.user,
                comment="Bla blabla",
            )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == f"{new_user_offerer.user.firstName} {new_user_offerer.user.lastName}"
        assert rows[0]["État"] == expected_status
        assert rows[0]["Date de la demande"] == "03/11/2022"
        assert rows[0]["Dernier commentaire"] == "Bla blabla"
        assert rows[0]["Tél Compte pro"] == new_user_offerer.user.phoneNumber
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name.upper()
        assert rows[0]["Date de création Structure"] == "02/11/2022"
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["SIREN"] == owner_user_offerer.offerer.siren

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_payload_content_no_action(self, authenticated_client):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 3), dateCreated=datetime.datetime(2022, 11, 24)
        )
        offerers_factories.UserOffererFactory(offerer=owner_user_offerer.offerer)  # other validated, not owner
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer, dateCreated=datetime.datetime(2022, 11, 25)
        )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == f"{new_user_offerer.user.firstName} {new_user_offerer.user.lastName}"
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Date de la demande"] == "25/11/2022"
        assert rows[0]["Dernier commentaire"] == ""
        assert rows[0]["Tél Compte pro"] == ""
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name.upper()
        assert rows[0]["Date de création Structure"] == "03/11/2022"
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["SIREN"] == owner_user_offerer.offerer.siren

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (31, {"per_page": 10}, 4, 1, 10),
            (31, {"per_page": 10, "page": 1}, 4, 1, 10),
            (31, {"per_page": 10, "page": 3}, 4, 3, 10),
            (31, {"per_page": 10, "page": 4}, 4, 4, 1),
            (20, {"per_page": 10, "page": 1}, 2, 1, 10),
            (27, {"page": 1}, 1, 1, 27),
            (10, {"per_page": 25, "page": 1}, 1, 1, 10),
        ),
    )
    def test_list_pagination(
        self, authenticated_client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        # given
        for _ in range(total_items):
            offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate", **pagination_config)
        )

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == expected_items
        assert html_parser.extract_pagination_info(response.data) == (
            expected_page,
            expected_total_pages,
            total_items,
        )

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @pytest.mark.parametrize(
        "status_filter, expected_status, expected_users_emails",
        (
            ("NEW", 200, {"a@example.com", "c@example.com", "e@example.com"}),
            ("PENDING", 200, {"b@example.com", "d@example.com", "f@example.com"}),
            (
                ["NEW", "PENDING"],
                200,
                {"a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"},
            ),
            ("VALIDATED", 200, {"g@example.com"}),
            ("REJECTED", 200, set()),
            (
                None,
                200,
                {"a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"},
            ),  # same as default
            ("OTHER", 400, set()),  # unknown value
        ),
    )
    def test_list_filtering_by_status(
        self, authenticated_client, status_filter, expected_status, expected_users_emails, user_offerer_to_be_validated
    ):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for(
                    "backoffice_v3_web.validate_offerer.list_offerers_attachments_to_validate", status=status_filter
                )
            )

        # then
        assert response.status_code == expected_status
        if expected_status == 200:
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Email Compte pro"] for row in rows} == expected_users_emails
        else:
            assert html_parser.count_table_rows(response.data) == 0


class ValidateOffererAttachmentUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.user_offerer.user_offerer_validate"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ValidateOffererAttachmentTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_validate_offerer_attachment(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_validate", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_validate_offerer_attachment_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_validate", user_offerer_id=42)
        )

        # then
        assert response.status_code == 404

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_cannot_validate_offerer_attachment_already_validated(self, authenticated_client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_validate", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 400

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà validé" in redirected_response.data.decode("utf8")


class RejectOffererAttachmentUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.user_offerer.user_offerer_reject"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class RejectOffererAttachmentTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_reject_offerer_attachment(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_reject", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 303

        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 0

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_reject_offerer_returns_404_if_offerer_attachment_is_not_found(self, authenticated_client):
        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_reject", user_offerer_id=42)
        )

        # then
        assert response.status_code == 404


class SetOffererAttachmentPendingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    method = "post"
    endpoint = "backoffice_v3_web.user_offerer.user_offerer_set_pending"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class SetOffererAttachmentPendingTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = authenticated_client.post(
            url_for("backoffice_v3_web.user_offerer.user_offerer_set_pending", user_offerer_id=user_offerer.id),
            form={"comment": "En attente de documents"},
        )

        # then
        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert user_offerer.validationStatus == offerers_models.ValidationStatus.PENDING
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"
