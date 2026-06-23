import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi.connectors.entreprise.models import SirenInfo
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.utils import siren as siren_utils


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


class CheckOffererSirenTaskTest:
    @patch("time.sleep")
    def test_active_offerer(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        offerers_tasks.check_offerer_siren_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert not offerer.tags

    @patch("pcapi.core.offerers.api.close_offerer")
    def test_still_active_offerer_closed_in_the_future(
        self,
        mock_close_offerer,
        client,
        siren_caduc_tag,
    ):
        offerer = offerers_factories.OffererFactory(siren="111222337")
        closure_date = datetime.date.today() + datetime.timedelta(days=7)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=True,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
            )

        assert not offerer.tags
        mock_close_offerer.assert_not_called()

    @patch("time.sleep")
    def test_untag_revalidated_offerer_still_tagged(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(tags=[siren_caduc_tag])
        offerers_factories.UserOffererFactory(offerer=offerer)

        offerers_tasks.check_offerer_siren_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
        assert action.comment == "L'entité juridique est détectée comme active via l'API Entreprise (données INSEE)"
        assert action.extraData == {"modified_info": {"tags": {"old_info": siren_caduc_tag.label}}}

    @patch("time.sleep")
    def test_active_offerer_waiting_for_validation(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.PendingOffererFactory()

        offerers_tasks.check_offerer_siren_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert offerer.isWaitingForValidation
        assert not offerer.tags

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_inactive_offerer_is_handled(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
            )

        mock_handle_closed_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    def test_inactive_offerer_not_closed_when_flag_is_false(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=False)
            )

        assert not offerer.tags
        mock_handle_closed_offerer.assert_not_called()

    @patch("time.sleep")
    def test_siren_not_found(self, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="000000000")

        offerers_tasks.check_offerer_siren_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert not offerer.tags

    def test_invalid_siren_format(self, client, caplog):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="123456789")

        offerers_tasks.check_offerer_siren_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=False)
        )

        assert caplog.records[0].message == "Invalid SIREN format in the database"


class FinalizeClosingVenueTaskTest:
    def test_bookings_have_been_deleted(self):
        venue = offerers_factories.VenueFactory()
        author = users_factories.BaseUserFactory()
        self.create_synced_offers_with_bookings(venue)

        payload = offerers_tasks.FinalizeClosingVenuePayload(venue_id=venue.id, author_id=author.id)
        offerers_tasks.finalize_closing_venue_task(payload.model_dump())

        db.session.refresh(venue)
        assert all(booking.isCancelled for booking in venue.bookings)
        assert all(booking.isCancelled for booking in venue.collectiveBookings)

    def test_new_history_entries_are_added(self):
        venue = offerers_factories.VenueFactory()
        author = users_factories.BaseUserFactory()
        self.create_synced_offers_with_bookings(venue)

        payload = offerers_tasks.FinalizeClosingVenuePayload(venue_id=venue.id, author_id=author.id)
        offerers_tasks.finalize_closing_venue_task(payload.model_dump())

        db.session.refresh(venue)

        history = db.session.query(history_models.ActionHistory).filter_by(venueId=venue.id).one()
        assert history.actionType == history_models.ActionType.VENUE_CLOSED

        assert venue.state == offerers_models.VenueState.CLOSED

    def test_pivots_have_been_deleted(self):
        venue = offerers_factories.VenueFactory()
        author = users_factories.BaseUserFactory()
        self.create_synced_offers_with_bookings(venue)

        payload = offerers_tasks.FinalizeClosingVenuePayload(venue_id=venue.id, author_id=author.id)
        offerers_tasks.finalize_closing_venue_task(payload.model_dump())

        db.session.refresh(venue)
        assert not venue.cinemaProviderPivot
        assert not venue.allocinePivot

        assert venue.state == offerers_models.VenueState.CLOSED

    def create_synced_offers_with_bookings(self, venue):
        boost_pivot = providers_factories.BoostCinemaProviderPivotFactory(venue=venue)
        now = datetime.datetime.now(datetime.UTC)

        bookings_factories.BookingFactory.create_batch(
            2, stock__offer__venue=venue, stock__offer__publicationDatetime=now
        )
        bookings_factories.BookingFactory.create_batch(
            3,
            stock__offer__venue=venue,
            stock__offer__publicationDatetime=now,
            stock__offer__lastProviderId=boost_pivot.providerId,
        )
