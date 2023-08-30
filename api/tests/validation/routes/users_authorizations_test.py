import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2


class CheckUserCanValidateBookingV2Test:
    @pytest.mark.usefixtures("db_session")
    def test_ok_if_user_offerer(self):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        # The following call should not raise.
        check_user_can_validate_bookings_v2(user, offerer.id)

    def test_error_if_non_offerer(self):
        user = User()
        with pytest.raises(ApiErrors) as errors:
            check_user_can_validate_bookings_v2(user, None)
        assert errors.value.errors["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]


@pytest.mark.usefixtures("db_session")
class CheckApiKeyAllowsToValidateBookingTest:
    def test_ok_if_api_key_is_related_to_offerer(self):
        key = offerers_factories.ApiKeyFactory(secret="foo")
        # The following should not raise
        check_api_key_allows_to_validate_booking(key, key.offererId)

    def test_raises_if_api_key_not_related_to_offerer(self):
        key = offerers_factories.ApiKeyFactory()
        other_offerer = offerers_factories.OffererFactory()
        with pytest.raises(ApiErrors) as errors:
            check_api_key_allows_to_validate_booking(key, other_offerer.id)
        assert errors.value.errors["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]
