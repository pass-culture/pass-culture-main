from unittest.mock import MagicMock

import pytest

from pcapi.local_providers import FnacStocks
from pcapi.local_providers import LibrairesStocks
from pcapi.local_providers import PraxielStocks
from pcapi.local_providers import TiteLiveStocks
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.models import ApiErrors
from pcapi.models import VenueProvider
from pcapi.repository import repository
from pcapi.use_cases.connect_venue_to_provider import connect_venue_to_provider
from pcapi.utils.human_ids import humanize

from tests.local_providers.provider_test_utils import TestLocalProvider


class WhenProviderIsLibraires:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_connect_venue_when_synchronization_is_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider('LibrairesStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True
        provider_type = LibrairesStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # When
        connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # Then
        libraires_venue_provider = VenueProvider.query.one()
        assert libraires_venue_provider.venue == venue

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_synchronization_is_not_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret='12345678912345')
        provider = activate_provider('LibrairesStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = False
        provider_class = LibrairesStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            print(connect_venue_to_provider(provider_class, stock_repository, venue_provider_payload, self.find_by_id))

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec LesLibraires n’est pas disponible pour le SIRET 12345678912345']

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_venue_has_no_siret(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)
        provider = activate_provider('LibrairesStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        provider_type = LibrairesStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec LesLibraires n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres.']


class WhenProviderIsTiteLive:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_connect_venue_when_synchronization_is_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider('TiteLiveStocks')

        repository.save(venue)

        provider_type = TiteLiveStocks

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # When
        connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # Then
        titelive_venue_provider = VenueProvider.query.one()
        assert titelive_venue_provider.venue == venue

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_synchronization_is_not_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret='12345678912345')
        provider = activate_provider('TiteLiveStocks')

        repository.save(venue)

        provider_type = TiteLiveStocks

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = False
        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec TiteLive'
            ' n’est pas disponible pour le SIRET 12345678912345']

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_venue_has_no_siret(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)
        provider = activate_provider('TiteLiveStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True
        provider_type = TiteLiveStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec TiteLive n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres.']


class WhenProviderIsFnac:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_connect_venue_when_synchronization_is_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider('FnacStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True
        provider_type = FnacStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # When
        connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # Then
        fnac_venue_provider = VenueProvider.query.one()
        assert fnac_venue_provider.venue == venue

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_synchronization_is_not_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret='12345678912345')
        provider = activate_provider('FnacStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = False
        provider_type = FnacStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec FNAC n’est pas disponible pour le SIRET 12345678912345']

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_venue_has_no_siret(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)
        provider = activate_provider('FnacStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        provider_type = FnacStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec FNAC n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres.']


class WhenProviderIsPraxiel:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_connect_venue_when_synchronization_is_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider('PraxielStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True
        provider_type = PraxielStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # When
        connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # Then
        praxiel_venue_provider = VenueProvider.query.one()
        assert praxiel_venue_provider.venue == venue

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_synchronization_is_not_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret='12345678912345')
        provider = activate_provider('PraxielStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = False
        provider_type = PraxielStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec Praxiel/Inférence n’est pas disponible pour le SIRET 12345678912345']

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_venue_has_no_siret(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)
        provider = activate_provider('PraxielStocks')

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        provider_type = PraxielStocks

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # then
        assert error.value.errors['provider'] == [
            'L’importation d’offres avec Praxiel/Inférence n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres.']


class WhenProviderIsSomethingElse:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_raise_an_error(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = create_provider(local_class='TestLocalProvider')
        repository.save(venue, provider)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        provider_type = TestLocalProvider

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # When
        with pytest.raises(ApiErrors) as error:
            connect_venue_to_provider(provider_type, stock_repository, venue_provider_payload, self.find_by_id)

        # Then
        assert error.value.errors['provider'] == ['Provider non pris en charge']
