import pytest

from models import ApiErrors, PcObject
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_provider
from utils.human_ids import humanize
from validation.venue_providers import validate_new_venue_provider_information


class ValidateNewVenueProviderInformationTest:
    @clean_database
    def test_returns_true_when_all_information_are_present_and_well_formed(self, app):
        # given
        provider = create_provider()
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer, is_admin=True)
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(provider, user_offerer, venue)

        payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
            'venueIdAtOfferProvider': '567890'
        }

        # when
        try:
            validate_new_venue_provider_information(payload)
        except ApiErrors:
            # then
            assert False

    def test_raise_errors_if_venue_id_at_offer_provider_is_missing(self, app):
        # given
        payload = {
            'providerId': 'A1',
            'venueId': 'B2',
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.errors['venueIdAtOfferProvider'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_venue_id_is_missing(self, app):
        # given
        payload = {
            'providerId': 'A1',
            'venueIdAtOfferProvider': '567890'
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.errors['venueId'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_provider_id_is_missing(self):
        # given
        payload = {
            'venueId': 'B2',
            'venueIdAtOfferProvider': '567890'
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.errors['providerId'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_json_payload_is_empty(self, app):
        # given
        payload = {}

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert len(errors.value.errors) == 3
        assert errors.value.errors['providerId'] == ['Ce champ est obligatoire']
        assert errors.value.errors['venueId'] == ['Ce champ est obligatoire']
        assert errors.value.errors['venueIdAtOfferProvider'] == ['Ce champ est obligatoire']

    def test_raise_errors_if_no_provider_found(self, app):
        # given
        payload = {
            'providerId': 'B9',
            'venueId': 'B9',
            'venueIdAtOfferProvider': '567890'
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.status_code == 400
        assert errors.value.errors['provider'] == ["Cette source n'est pas disponible"]

    @clean_database
    def test_raise_errors_if_provider_is_not_active(self, app):
        # given
        provider = create_provider(is_active=False)
        PcObject.save(provider)

        payload = {
            'providerId': humanize(provider.id),
            'venueId': 'B9',
            'venueIdAtOfferProvider': '567890'
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.status_code == 400
        assert errors.value.errors['provider'] == ["Cette source n'est pas disponible"]

    @clean_database
    def test_raise_errors_if_provider_is_not_enable_for_pro(self, app):
        # given
        provider = create_provider(is_enable_for_pro=False)
        PcObject.save(provider)

        payload = {
            'providerId': humanize(provider.id),
            'venueId': 'B9',
            'venueIdAtOfferProvider': '567890'
        }

        # when
        with pytest.raises(ApiErrors) as errors:
            validate_new_venue_provider_information(payload)

        # then
        assert errors.value.status_code == 400
        assert errors.value.errors['provider'] == ["Cette source n'est pas disponible"]
