import pytest

from validation.routes.seen_offers import check_payload_is_valid, PayloadMissing


class checkPayloadIsValidTest:
    def test_should_raise_payload_missing_if_missing_offer_id(self):
        # given
        payload = {}

        # when
        with pytest.raises(PayloadMissing) as error:
            check_payload_is_valid(payload)

        # then
        assert error.value.errors['global'] == ['Données manquantes']


    def test_should_not_raise_payload_error(self):
        # given
        payload = {"offerId": "AE"}

        # when
        check = check_payload_is_valid(payload)

        # then
        assert check is None
