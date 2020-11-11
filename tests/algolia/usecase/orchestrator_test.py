from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from algoliasearch.exceptions import AlgoliaException
from freezegun import freeze_time
import pytest

from pcapi.algolia.usecase.orchestrator import delete_expired_offers
from pcapi.algolia.usecase.orchestrator import process_eligible_offers
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


TOMORROW = datetime.now() + timedelta(days=1)


class ProcessEligibleOffersTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.algolia.usecase.orchestrator.add_offer_ids_in_error")
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.build_object", return_value={"fake": "test"})
    def test_should_add_objects_when_objects_are_eligible_and_not_already_indexed(
        self,
        mock_build_object,
        mock_check_offer_exists,
        mock_add_objects,
        mock_delete_objects,
        mock_add_to_indexed_offers,
        mock_delete_indexed_offers,
        mock_add_offer_ids_in_error,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=10)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=False)
        stock3 = create_stock(booking_limit_datetime=TOMORROW, offer=offer3, quantity=10)
        repository.save(stock1, stock2, stock3)
        mock_check_offer_exists.side_effect = [False, False, False]

        # When
        process_eligible_offers(client=client, offer_ids=[offer1.id, offer2.id], from_provider_update=False)

        # Then
        assert mock_build_object.call_count == 2
        mock_add_objects.assert_called_once_with(objects=[{"fake": "test"}, {"fake": "test"}])
        assert mock_add_to_indexed_offers.call_count == 2
        assert mock_add_to_indexed_offers.call_args_list == [
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "Test Book", "dates": [], "prices": [10.0]},
                offer_id=offer1.id,
            ),
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "Test Book", "dates": [], "prices": [10.0]},
                offer_id=offer2.id,
            ),
        ]
        mock_delete_indexed_offers.assert_not_called()
        mock_delete_objects.assert_not_called()
        mock_pipeline.execute.assert_called_once()
        mock_pipeline.reset.assert_called_once()
        mock_add_offer_ids_in_error.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.algolia.usecase.orchestrator.add_offer_ids_in_error")
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object", return_value={"fake": "test"})
    def test_should_delete_objects_when_objects_are_not_eligible_and_were_already_indexed(
        self,
        mock_build_object,
        mock_add_objects,
        mock_delete_objects,
        mock_add_to_indexed_offers,
        mock_check_offer_exists,
        mock_delete_indexed_offers,
        mock_add_offer_ids_in_error,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=0)
        repository.save(stock1, stock2)
        mock_check_offer_exists.side_effect = [True, True]

        # When
        process_eligible_offers(client=client, offer_ids=[offer1.id, offer2.id], from_provider_update=False)

        # Then
        mock_build_object.assert_not_called()
        mock_add_objects.assert_not_called()
        mock_add_to_indexed_offers.assert_not_called()
        mock_delete_objects.assert_called_once()
        assert mock_delete_objects.call_args_list == [call(object_ids=[humanize(offer1.id), humanize(offer2.id)])]
        mock_delete_indexed_offers.assert_called_once()
        assert mock_delete_indexed_offers.call_args_list == [call(client=client, offer_ids=[offer1.id, offer2.id])]
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_not_called()
        mock_add_offer_ids_in_error.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object", return_value={"fake": "test"})
    def test_should_not_delete_objects_when_objects_are_not_eligible_and_were_not_indexed(
        self,
        mock_build_object,
        mock_add_objects,
        mock_delete_objects,
        mock_add_to_indexed_offers,
        mock_check_offer_exists,
        mock_delete_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=0)
        repository.save(stock1, stock2)
        mock_check_offer_exists.side_effect = [False, False]

        # When
        process_eligible_offers(client=client, offer_ids=[offer1.id, offer2.id], from_provider_update=False)

        # Then
        mock_build_object.assert_not_called()
        mock_add_objects.assert_not_called()
        mock_add_to_indexed_offers.assert_not_called()
        mock_delete_objects.assert_not_called()
        mock_delete_indexed_offers.assert_not_called()
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.algolia.usecase.orchestrator.add_offer_ids_in_error")
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object", return_value={"fake": "test"})
    def test_should_add_offer_ids_in_error_when_deleting_objects_failed(
        self,
        mock_build_object,
        mock_add_objects,
        mock_delete_objects,
        mock_add_to_indexed_offers,
        mock_check_offer_exists,
        mock_delete_indexed_offers,
        mock_add_offer_ids_in_error,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=0)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=0)
        repository.save(stock1, stock2)
        mock_check_offer_exists.side_effect = [True, True]
        mock_delete_objects.side_effect = [AlgoliaException]

        # When
        process_eligible_offers(client=client, offer_ids=[offer1.id, offer2.id], from_provider_update=False)

        # Then
        mock_build_object.assert_not_called()
        mock_add_objects.assert_not_called()
        mock_add_to_indexed_offers.assert_not_called()
        mock_delete_objects.assert_called_once()
        assert mock_delete_objects.call_args_list == [call(object_ids=[humanize(offer1.id), humanize(offer2.id)])]
        mock_delete_indexed_offers.assert_not_called()
        mock_add_offer_ids_in_error.assert_called_once_with(client=client, offer_ids=[offer1.id, offer2.id])
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_not_called()

    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.get_offer_details")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @pytest.mark.usefixtures("db_session")
    def test_should_index_offers_that_are_not_already_indexed(
        self,
        mock_add_objects,
        mock_build_object,
        mock_delete_objects,
        mock_check_offer_exists,
        mock_get_offer_details,
        mock_add_to_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name="super offre 1", venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=1)
        offer2 = create_offer_with_thing_product(thing_name="super offre 2", venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=1)
        offer3 = create_offer_with_thing_product(thing_name="super offre 3", venue=venue, is_active=True)
        stock3 = create_stock(booking_limit_datetime=TOMORROW, offer=offer3, quantity=1)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        mock_build_object.side_effect = [
            {"fake": "object"},
            {"fake": "object"},
            {"fake": "object"},
        ]
        mock_check_offer_exists.side_effect = [False, False, False]

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 3
        assert mock_get_offer_details.call_count == 0
        assert mock_add_to_indexed_offers.call_count == 3
        assert mock_add_to_indexed_offers.call_args_list == [
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "super offre 1", "dates": [], "prices": [10.0]},
                offer_id=offer1.id,
            ),
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "super offre 2", "dates": [], "prices": [10.0]},
                offer_id=offer2.id,
            ),
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "super offre 3", "dates": [], "prices": [10.0]},
                offer_id=offer3.id,
            ),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [
            call(objects=[{"fake": "object"}, {"fake": "object"}, {"fake": "object"}])
        ]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.get_offer_details")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @pytest.mark.usefixtures("db_session")
    def test_should_delete_offers_that_are_already_indexed(
        self,
        mock_add_objects,
        mock_build_object,
        mock_delete_objects,
        mock_check_offer_exists,
        mock_get_offer_details,
        mock_add_to_indexed_offers,
        mock_delete_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name="super offre 1", venue=venue, is_active=False)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=1)
        offer2 = create_offer_with_thing_product(thing_name="super offre 2", venue=venue, is_active=False)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=1)
        offer3 = create_offer_with_thing_product(thing_name="super offre 3", venue=venue, is_active=False)
        stock3 = create_stock(booking_limit_datetime=TOMORROW, offer=offer3, quantity=1)
        repository.save(stock1, stock2, stock3)
        offer_ids = [offer1.id, offer2.id, offer3.id]
        mock_check_offer_exists.side_effect = [True, True, True]

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 3
        assert mock_build_object.call_count == 0
        assert mock_add_objects.call_count == 0
        assert mock_get_offer_details.call_count == 0
        assert mock_add_to_indexed_offers.call_count == 0
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [
            call(object_ids=[humanize(offer1.id), humanize(offer2.id), humanize(offer3.id)])
        ]
        assert mock_delete_indexed_offers.call_count == 1
        assert mock_delete_indexed_offers.call_args_list == [
            call(client=client, offer_ids=[offer1.id, offer2.id, offer3.id])
        ]
        assert mock_pipeline.execute.call_count == 0
        assert mock_pipeline.reset.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_delete_offers_that_are_not_already_indexed(
        self, mock_delete_objects, mock_check_offer_exists, mock_delete_indexed_offers, app
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name="super offre 1", venue=venue, is_active=False)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=1)
        offer2 = create_offer_with_thing_product(thing_name="super offre 2", venue=venue, is_active=False)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=1)
        repository.save(stock1, stock2)
        offer_ids = [offer1.id, offer2.id]
        mock_check_offer_exists.side_effect = [False, False]

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 2
        assert mock_delete_objects.call_count == 0
        assert mock_delete_indexed_offers.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.get_offer_details")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @pytest.mark.usefixtures("db_session")
    def test_should_reindex_offers_that_are_already_indexed_only_if_offer_name_changed(
        self,
        mock_add_objects,
        mock_build_object,
        mock_delete_objects,
        mock_check_offer_exists,
        mock_get_offer_details,
        mock_add_to_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name="super offre 1", venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=1)
        repository.save(stock1)
        offer_ids = [offer1.id]
        mock_build_object.side_effect = [
            {"fake": "object"},
        ]
        mock_check_offer_exists.return_value = True
        mock_get_offer_details.return_value = {"name": "une autre super offre", "dates": [], "prices": [11.0]}

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 1
        assert mock_get_offer_details.call_count == 1
        assert mock_add_to_indexed_offers.call_count == 1
        assert mock_add_to_indexed_offers.call_args_list == [
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "super offre 1", "dates": [], "prices": [10.0]},
                offer_id=offer1.id,
            ),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [call(objects=[{"fake": "object"}])]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.get_offer_details")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_reindex_offers_that_are_already_indexed_if_offer_name_has_not_changed(
        self,
        mock_add_objects,
        mock_build_object,
        mock_delete_objects,
        mock_check_offer_exists,
        mock_get_offer_details,
        mock_add_to_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(thing_name="super offre 1", venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=1)
        repository.save(stock1)
        offer_ids = [offer1.id]
        mock_build_object.side_effect = [
            {"fake": "object"},
        ]
        mock_check_offer_exists.return_value = True
        mock_get_offer_details.return_value = {"name": "super offre 1", "dates": [], "prices": [10.0]}

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 1
        assert mock_get_offer_details.call_count == 1
        assert mock_add_to_indexed_offers.call_count == 0
        assert mock_add_objects.call_count == 0
        assert mock_pipeline.execute.call_count == 0
        assert mock_pipeline.reset.call_count == 0
        assert mock_delete_objects.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.get_offer_details")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.build_object")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2019-01-01 12:00:00")
    def test_should_reindex_offers_only_when_stocks_beginning_datetime_have_changed(
        self,
        mock_add_objects,
        mock_build_object,
        mock_delete_objects,
        mock_check_offer_exists,
        mock_get_offer_details,
        mock_add_to_indexed_offers,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(
            date_created=datetime(2019, 1, 1), event_name="super offre 1", venue=venue, is_active=True
        )
        stock = create_stock(
            beginning_datetime=datetime(2019, 1, 5),
            booking_limit_datetime=datetime(2019, 1, 3),
            offer=offer,
            quantity=1,
        )
        repository.save(stock)
        offer_ids = [offer.id]
        mock_build_object.side_effect = [
            {"fake": "object"},
        ]
        mock_check_offer_exists.return_value = True
        mock_get_offer_details.return_value = {"name": "super offre 1", "dates": [1515542400.0], "prices": [10.0]}

        # When
        process_eligible_offers(client=client, offer_ids=offer_ids, from_provider_update=True)

        # Then
        assert mock_check_offer_exists.call_count == 1
        assert mock_get_offer_details.call_count == 1
        assert mock_add_to_indexed_offers.call_count == 1
        assert mock_add_to_indexed_offers.call_args_list == [
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "super offre 1", "dates": [1546646400.0], "prices": [10.0]},
                offer_id=offer.id,
            ),
        ]
        assert mock_add_objects.call_count == 1
        assert mock_add_objects.call_args_list == [call(objects=[{"fake": "object"}])]
        assert mock_pipeline.execute.call_count == 1
        assert mock_pipeline.reset.call_count == 1
        assert mock_delete_objects.call_count == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.algolia.usecase.orchestrator.add_offer_ids_in_error")
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.add_to_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    @patch("pcapi.algolia.usecase.orchestrator.add_objects")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.build_object", return_value={"fake": "test"})
    def test_should_add_offer_ids_in_error_when_adding_objects_failed(
        self,
        mock_build_object,
        mock_check_offer_exists,
        mock_add_objects,
        mock_delete_objects,
        mock_add_to_indexed_offers,
        mock_delete_indexed_offers,
        mock_add_offer_ids_in_error,
        app,
    ):
        # Given
        client = MagicMock()
        client.pipeline = MagicMock()
        client.pipeline.return_value = MagicMock()
        mock_pipeline = client.pipeline()
        mock_pipeline.execute = MagicMock()
        mock_pipeline.reset = MagicMock()
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(booking_limit_datetime=TOMORROW, offer=offer1, quantity=10)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=True)
        stock2 = create_stock(booking_limit_datetime=TOMORROW, offer=offer2, quantity=10)
        repository.save(stock1, stock2)
        mock_check_offer_exists.side_effect = [False, False]
        mock_add_objects.side_effect = [AlgoliaException]

        # When
        process_eligible_offers(client=client, offer_ids=[offer1.id, offer2.id], from_provider_update=False)

        # Then
        assert mock_build_object.call_count == 2
        mock_add_objects.assert_called_once_with(objects=[{"fake": "test"}, {"fake": "test"}])
        assert mock_add_to_indexed_offers.call_count == 2
        assert mock_add_to_indexed_offers.call_args_list == [
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "Test Book", "dates": [], "prices": [10.0]},
                offer_id=offer1.id,
            ),
            call(
                pipeline=mock_pipeline,
                offer_details={"name": "Test Book", "dates": [], "prices": [10.0]},
                offer_id=offer2.id,
            ),
        ]
        mock_delete_indexed_offers.assert_not_called()
        mock_delete_objects.assert_not_called()
        mock_pipeline.execute.assert_not_called()
        mock_pipeline.reset.assert_called_once()
        assert mock_add_offer_ids_in_error.call_args_list == [call(client=client, offer_ids=[offer1.id, offer2.id])]


class DeleteExpiredOffersTest:
    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    def test_should_delete_expired_offers_from_algolia_when_at_least_one_offer_id_and_offers_were_indexed(
        self, mock_delete_objects, mock_check_offer_exists, mock_delete_indexed_offers, app
    ):
        # Given
        client = MagicMock()
        mock_check_offer_exists.side_effect = [True, True, True]

        # When
        delete_expired_offers(client=client, offer_ids=[1, 2, 3])

        # Then
        assert mock_delete_objects.call_count == 1
        assert mock_delete_objects.call_args_list == [call(object_ids=["AE", "A9", "AM"])]
        assert mock_delete_indexed_offers.call_count == 1
        assert mock_delete_indexed_offers.call_args_list == [call(client=client, offer_ids=[1, 2, 3])]

    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    def test_should_not_delete_expired_offers_from_algolia_when_no_offer_id(
        self, mock_delete_objects, mock_delete_indexed_offers, app
    ):
        # Given
        client = MagicMock()

        # When
        delete_expired_offers(client=client, offer_ids=[])

        # Then
        assert mock_delete_objects.call_count == 0
        assert mock_delete_indexed_offers.call_count == 0

    @patch("pcapi.algolia.usecase.orchestrator.delete_indexed_offers")
    @patch("pcapi.algolia.usecase.orchestrator.check_offer_exists")
    @patch("pcapi.algolia.usecase.orchestrator.delete_objects")
    def test_should_not_delete_expired_offers_from_algolia_when_at_least_one_offer_id_but_offers_were_not_indexed(
        self, mock_delete_objects, mock_check_offer_exists, mock_delete_indexed_offers, app
    ):
        # Given
        client = MagicMock()
        mock_check_offer_exists.side_effect = [False, False, False]

        # When
        delete_expired_offers(client=client, offer_ids=[])

        # Then
        assert mock_delete_objects.call_count == 0
        assert mock_delete_indexed_offers.call_count == 0
