import logging
from unittest.mock import patch

import pytest
import sqlalchemy as sa

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.scripts.handle_regul_for_venues_with_rejected_offers.main import main


pytestmark = pytest.mark.usefixtures("db_session")

SCRIPT_MODULE = "pcapi.scripts.handle_regul_for_venues_with_rejected_offers.main"


def _create_eligible_venue(**kwargs):
    """Create a venue that passes all validation checks: non-permanent, no SIRET, not open to public."""
    defaults = dict(siret=None, comment="no siret", isPermanent=False, isOpenToPublic=False)
    defaults.update(kwargs)
    return offerers_factories.VenueFactory(**defaults)


def _get_venue(venue_id: int, include_deleted: bool = False) -> offerers_models.Venue:
    stmt = sa.select(offerers_models.Venue).where(offerers_models.Venue.id == venue_id)
    if include_deleted:
        stmt = stmt.execution_options(include_deleted=True)
    return db.session.scalars(stmt).one()


class ValidateVenueTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_siret(self, read_venue_ids_mock, caplog):
        venue = offerers_factories.VenueFactory(isPermanent=False, isOpenToPublic=False)
        assert venue.siret is not None
        offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue validation failed, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["venue_id"] == venue_id
        assert warning_records[0].extra["reason"] == "Venue has a SIRET"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_permanent_venue(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue(isPermanent=True)
        offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue validation failed, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue is permanent"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_open_to_public(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue(isOpenToPublic=True)
        offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue validation failed, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue is open to public"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_not_found(self, read_venue_ids_mock, caplog):
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [999999]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        warning_records = [r for r in caplog.records if r.message == "Venue not found, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["venue_id"] == 999999


class CheckOffersTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_non_rejected_individual_offer(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue has non-rejected offers, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue has non-rejected individual offers"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_non_rejected_collective_offer(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        educational_factories.CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue has non-rejected offers, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue has non-rejected collective offers"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_non_rejected_collective_offer_template(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, validation=OfferValidationStatus.APPROVED)
        author = users_factories.UserFactory()
        venue_id = venue.id
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue has non-rejected offers, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue has non-rejected collective offer templates"


class CheckBookingsTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_individual_bookings(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        venue_id = venue.id
        bookings_factories.BookingFactory(
            stock__offer__venue=venue,
            stock__offer__validation=OfferValidationStatus.REJECTED,
        )
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue has bookings, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue has individual bookings"

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_venue_with_collective_bookings(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        venue_id = venue.id
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__validation=OfferValidationStatus.REJECTED,
        )
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id)
        assert not venue.isSoftDeleted
        warning_records = [r for r in caplog.records if r.message == "Venue has bookings, skipping"]
        assert len(warning_records) == 1
        assert warning_records[0].extra["reason"] == "Venue has collective bookings"


class DeleteRejectedOffersTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_deletes_rejected_individual_offers_and_soft_deletes_venue(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        stock = offers_factories.StockFactory(offer=offer)
        offer_id = offer.id
        stock_id = stock.id
        venue_id = venue.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id, include_deleted=True)
        assert venue.isSoftDeleted
        assert db.session.scalar(sa.select(offers_models.Offer.id).where(offers_models.Offer.id == offer_id)) is None
        assert db.session.scalar(sa.select(offers_models.Stock.id).where(offers_models.Stock.id == stock_id)) is None

        deleted_records = [r for r in caplog.records if r.message == "Deleted rejected offers for venue"]
        assert len(deleted_records) == 1
        assert deleted_records[0].extra["venue_id"] == venue_id
        assert deleted_records[0].extra["deleted_individual_offer_ids"] == [offer_id]
        assert deleted_records[0].extra["deleted_collective_offer_ids"] == []
        assert deleted_records[0].extra["deleted_template_ids"] == []

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_deletes_rejected_collective_offers_and_soft_deletes_venue(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        collective_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, validation=OfferValidationStatus.REJECTED
        )
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        venue_id = venue.id
        collective_offer_id = collective_offer.id
        collective_stock_id = collective_stock.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id, include_deleted=True)
        assert venue.isSoftDeleted
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectiveOffer.id).where(
                    educational_models.CollectiveOffer.id == collective_offer_id
                )
            )
            is None
        )
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectiveStock.id).where(
                    educational_models.CollectiveStock.id == collective_stock_id
                )
            )
            is None
        )

        deleted_records = [r for r in caplog.records if r.message == "Deleted rejected offers for venue"]
        assert len(deleted_records) == 1
        assert deleted_records[0].extra["deleted_individual_offer_ids"] == []
        assert deleted_records[0].extra["deleted_collective_offer_ids"] == [collective_offer_id]
        assert deleted_records[0].extra["deleted_template_ids"] == []

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_deletes_rejected_collective_offer_templates_and_related_objects(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, validation=OfferValidationStatus.REJECTED
        )
        offer_request = educational_factories.CollectiveOfferRequestFactory(collectiveOfferTemplate=template)
        playlist = educational_factories.PlaylistFactory(collective_offer_template=template)
        redactor = educational_factories.EducationalRedactorFactory()
        favorite = educational_models.CollectiveOfferTemplateEducationalRedactor(
            educationalRedactorId=redactor.id,
            collectiveOfferTemplateId=template.id,
        )
        db.session.add(favorite)
        db.session.flush()
        other_venue = offerers_factories.VenueFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(venue=other_venue, template=template)
        venue_id = venue.id
        template_id = template.id
        offer_request_id = offer_request.id
        playlist_id = playlist.id
        favorite_id = favorite.id
        collective_offer_id = collective_offer.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id, include_deleted=True)
        assert venue.isSoftDeleted
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectiveOfferTemplate.id).where(
                    educational_models.CollectiveOfferTemplate.id == template_id
                )
            )
            is None
        )
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectiveOfferRequest.id).where(
                    educational_models.CollectiveOfferRequest.id == offer_request_id
                )
            )
            is None
        )
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectivePlaylist.id).where(
                    educational_models.CollectivePlaylist.id == playlist_id
                )
            )
            is None
        )
        assert (
            db.session.scalar(
                sa.select(educational_models.CollectiveOfferTemplateEducationalRedactor.id).where(
                    educational_models.CollectiveOfferTemplateEducationalRedactor.id == favorite_id
                )
            )
            is None
        )
        collective_offer = db.session.scalars(
            sa.select(educational_models.CollectiveOffer).where(
                educational_models.CollectiveOffer.id == collective_offer_id
            )
        ).one()
        assert collective_offer.templateId is None

        deleted_records = [r for r in caplog.records if r.message == "Deleted rejected offers for venue"]
        assert len(deleted_records) == 1
        assert deleted_records[0].extra["deleted_individual_offer_ids"] == []
        assert deleted_records[0].extra["deleted_collective_offer_ids"] == []
        assert deleted_records[0].extra["deleted_template_ids"] == [template_id]


class SoftDeleteVenueTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_soft_deletes_venue_without_offers(self, read_venue_ids_mock, caplog):
        venue = _create_eligible_venue()
        venue_id = venue.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue = _get_venue(venue_id, include_deleted=True)
        assert venue.isSoftDeleted

        soft_delete_records = [r for r in caplog.records if r.message == "Venue soft deleted"]
        assert len(soft_delete_records) == 1
        assert soft_delete_records[0].extra["venue_id"] == venue_id

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_creates_action_history_with_author(self, read_venue_ids_mock):
        venue = _create_eligible_venue()
        venue_id = venue.id
        author = users_factories.UserFactory()
        author_id = author.id
        read_venue_ids_mock.return_value = [venue_id]

        main(not_dry=True, author=author)

        action = db.session.scalars(
            sa.select(history_models.ActionHistory).where(history_models.ActionHistory.venueId == venue_id)
        ).one()
        assert action.actionType == history_models.ActionType.VENUE_SOFT_DELETED
        assert action.authorUserId == author_id
        assert action.venueId == venue_id


class MainTest:
    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_processes_multiple_venues(self, read_venue_ids_mock, caplog):
        venue1 = _create_eligible_venue()
        venue2 = _create_eligible_venue()
        offers_factories.OfferFactory(venue=venue1, validation=OfferValidationStatus.REJECTED)
        offers_factories.OfferFactory(venue=venue2, validation=OfferValidationStatus.REJECTED)
        venue1_id = venue1.id
        venue2_id = venue2.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [venue1_id, venue2_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        venue1 = _get_venue(venue1_id, include_deleted=True)
        venue2 = _get_venue(venue2_id, include_deleted=True)
        assert venue1.isSoftDeleted
        assert venue2.isSoftDeleted

        completed_records = [r for r in caplog.records if r.message == "Script completed"]
        assert len(completed_records) == 1
        assert completed_records[0].extra["processed"] == 2
        assert completed_records[0].extra["skipped"] == 0
        assert completed_records[0].extra["total"] == 2

    @patch(f"{SCRIPT_MODULE}._read_venue_ids")
    def test_skips_invalid_venue_but_processes_valid_ones(self, read_venue_ids_mock, caplog):
        valid_venue = _create_eligible_venue()
        invalid_venue = _create_eligible_venue(isPermanent=True)
        valid_venue_id = valid_venue.id
        invalid_venue_id = invalid_venue.id
        author = users_factories.UserFactory()
        read_venue_ids_mock.return_value = [invalid_venue_id, valid_venue_id]

        with caplog.at_level(logging.INFO):
            main(not_dry=True, author=author)

        valid_venue = _get_venue(valid_venue_id, include_deleted=True)
        invalid_venue = _get_venue(invalid_venue_id)
        assert valid_venue.isSoftDeleted
        assert not invalid_venue.isSoftDeleted

        completed_records = [r for r in caplog.records if r.message == "Script completed"]
        assert len(completed_records) == 1
        assert completed_records[0].extra["processed"] == 1
        assert completed_records[0].extra["skipped"] == 1
        assert completed_records[0].extra["total"] == 2
