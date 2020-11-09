import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.validation.routes.venue_providers import check_new_venue_provider_information


class ValidateNewVenueProviderInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_true_when_all_information_are_present_and_well_formed(self, app):
        # given
        provider = create_provider()
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer, is_admin=True)
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        repository.save(provider, user_offerer, venue)

        payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
        }

        # when
        try:
            check_new_venue_provider_information(payload)
        except ApiErrors:
            # then
            assert False

    def test_raise_errors_if_venue_id_is_missing(self, app):
        # given
        payload = {
            'providerId': 'A1',
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            check_new_venue_provider_information(payload)

        # then
        assert errors.value.errors['venueId'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_provider_id_is_missing(self):
        # given
        payload = {
            'venueId': 'B2',
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            check_new_venue_provider_information(payload)

        # then
        assert errors.value.errors['providerId'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_json_payload_is_empty(self, app):
        # given
        payload = {}

        # when
        with pytest.raises(ApiErrors) as errors:
            check_new_venue_provider_information(payload)

        # then
        assert len(errors.value.errors) == 2
        assert errors.value.errors['providerId'] == ['Ce champ est obligatoire']
        assert errors.value.errors['venueId'] == ['Ce champ est obligatoire']
