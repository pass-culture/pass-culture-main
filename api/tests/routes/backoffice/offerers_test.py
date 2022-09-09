# pylint: disable=redefined-outer-name
import datetime

from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture
def offerer():
    offerer = offerers_factories.OffererFactory(postalCode="46150")
    return offerer


@pytest.fixture
def venue_with_accepted_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture
def venue_with_draft_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.DRAFT,
    )
    return venue


@pytest.fixture
def venue_with_rejected_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.REJECTED,
    )
    return venue


@pytest.fixture
def venue_with_no_bank_info(offerer):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    return venue


@pytest.fixture
def venue_with_accepted_self_reimbursement_point(venue_with_accepted_bank_info):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_accepted_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_accepted_bank_info


@pytest.fixture
def venue_with_accepted_reimbursement_point(
    venue_with_accepted_bank_info,
    venue_with_no_bank_info,
):
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue_with_no_bank_info,
        reimbursementPoint=venue_with_accepted_bank_info,
    )
    return venue_with_no_bank_info


@pytest.fixture
def venue_with_expired_reimbursement_point(
    offerer,
    venue_with_accepted_bank_info,
):
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=venue,
        reimbursementPoint=venue_with_accepted_bank_info,
        timespan=[
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            datetime.datetime.utcnow() - datetime.timedelta(days=1),
        ],
    )
    return venue


@pytest.fixture
def venue_with_educational_status(offerer):
    educational_status = offerers_factories.VenueEducationalStatusFactory()
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        venueEducationalStatusId=educational_status.id,
    )
    return venue


@pytest.fixture
def random_venue():
    venue = offerers_factories.VenueFactory()
    finance_factories.BankInformationFactory(venue=venue)
    return venue


@pytest.fixture
def offerer_bank_info_with_application_id(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId="42")
    return bank_info


@pytest.fixture
def offerer_bank_info_with_no_application_id(offerer):
    bank_info = finance_factories.BankInformationFactory(offerer=offerer, applicationId=None)
    return bank_info


@pytest.fixture
def offerer_active_individual_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(5)
    ] + [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(5)
    ]
    return offers


@pytest.fixture
def offerer_inactive_individual_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(5)
    ] + [
        offers_factories.OfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(5)
    ]
    return offers


@pytest.fixture
def offerer_active_collective_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(5)
    ] + [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=True,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(5)
    ]
    return offers


@pytest.fixture
def offerer_inactive_collective_offers(offerer, venue_with_accepted_bank_info):
    offers = [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        for _ in range(5)
    ] + [
        educational_factories.CollectiveOfferFactory(
            venue=venue_with_accepted_bank_info,
            isActive=False,
            validation=offers_models.OfferValidationStatus.REJECTED.value,
        )
        for _ in range(5)
    ]
    return offers


@pytest.fixture
def offerer_stocks(offerer_active_individual_offers):
    stocks = [offers_factories.StockFactory(offer=offer) for offer in offerer_active_individual_offers]
    return stocks


@pytest.fixture
def individual_offerer_bookings(offerer_stocks):
    used_simple = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.USED,
        quantity=1,
        amount=10,
        stock=offerer_stocks[0],
    )
    confirmed_duo = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.CONFIRMED,
        quantity=2,
        amount=10,
        stock=offerer_stocks[1],
    )
    cancelled = bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.CANCELLED,
        venue=venue_with_accepted_bank_info,
        stock=offerer_stocks[2],
    )
    return [used_simple, confirmed_duo, cancelled]


@pytest.fixture
def collective_offerer_booking(venue_with_educational_status):
    stock = educational_factories.CollectiveStockFactory(price=1664)
    used = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock=stock,
        offerer=venue_with_educational_status.managingOfferer,
    )
    cancelled = educational_factories.CancelledCollectiveBookingFactory(
        collectiveStock=stock,
        offerer=venue_with_educational_status.managingOfferer,
    )
    return used, cancelled


class GetOffererUsersTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_list(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(), validationToken="not-validated"
        )

        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer2, user=users_factories.ProFactory())

        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == [
            {
                "id": uo1.user.id,
                "firstName": None,
                "lastName": None,
                "email": uo1.user.email,
            },
            {
                "id": uo2.user.id,
                "firstName": "Jean",
                "lastName": "Bon",
                "email": uo2.user.email,
            },
        ]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_empty_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_without_permission(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        auth_token = generate_token(users_factories.UserFactory(), [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_as_anonymous(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id))

        # then
        assert response.status_code == 403


class GetOfferBasicInfoTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_payload_structure(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert "data" in response.json
        payload = response.json["data"]
        assert "id" in payload
        assert "name" in payload
        assert "isActive" in payload
        assert "siren" in payload
        assert "region" in payload
        assert "bankInformationStatus" in payload
        assert "ko" in payload["bankInformationStatus"]
        assert "ok" in payload["bankInformationStatus"]
        assert "isCollectiveEligible" in payload
        assert "dmsUrl" in payload

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_basic_info(self, client, offerer):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        payload = response.json["data"]
        assert payload["id"] == offerer.id
        assert payload["name"] == offerer.name
        assert payload["isActive"] == offerer.isActive
        assert payload["siren"] == offerer.siren
        assert payload["region"] == "Occitanie"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_contains_venue_bank_information_stats(
        self,
        client,
        offerer,
        venue_with_accepted_self_reimbursement_point,
        venue_with_accepted_reimbursement_point,
        venue_with_expired_reimbursement_point,
        venue_with_rejected_bank_info,
        random_venue,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        bank_info_stats = response.json["data"]["bankInformationStatus"]
        assert bank_info_stats["ko"] == 2
        assert bank_info_stats["ok"] == 2

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_with_educational_venue_is_collective_eligible(
        self,
        client,
        offerer,
        venue_with_educational_status,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["isCollectiveEligible"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_with_no_educational_venue_is_not_collective_eligible(
        self,
        client,
        offerer,
        venue_with_accepted_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["isCollectiveEligible"] is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_returns_404_if_offerer_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=42)
        )

        # then
        assert response.status_code == 404

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403


class GetOffererTotalRevenueTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue(
        self,
        client,
        offerer,
        individual_offerer_bookings,
        collective_offerer_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 1694.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_individual_bookings_only(
        self,
        client,
        offerer,
        individual_offerer_bookings,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 30.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_collective_bookings_only(
        self,
        client,
        offerer,
        collective_offerer_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 1664.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_no_booking(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_returns_0_if_offerer_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403


class GetOffererOffersStatsTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats(
        self,
        client,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 5
        assert offer_stats["active"]["collective"] == 5
        assert offer_stats["inactive"]["individual"] == 5
        assert offer_stats["inactive"]["collective"] == 5

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_0_if_no_offer(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_0_if_offerer_not_found(
        self,
        client,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_offers_stats_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_offers_stats_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403
