from flask_login import AnonymousUserMixin
import pytest

from pcapi.core.offerers.models import ApiKey
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.validation.routes.users_authorizations import check_api_key_allows_to_validate_booking
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings_v2


class CheckUserCanValidateBookingTest:
    @pytest.mark.usefixtures("db_session")
    def test_check_user_offerer_can_validate_bookings(self):
        user_offerer = offers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        assert check_user_can_validate_bookings(user, offerer.id)

    def test_check_anonymous_user_cannot_validate_bookings(self):
        anonymous = AnonymousUserMixin()
        result = check_user_can_validate_bookings(anonymous, offerer_id=1)
        assert result is False

    def test_check_non_offerer_raise_error(self):
        user = User()
        with pytest.raises(ApiErrors) as errors:
            check_user_can_validate_bookings(user, None)
        assert errors.value.errors["global"] == ["Cette contremarque n'a pas été trouvée"]


class CheckUserCanValidateBookingV2Test:
    @pytest.mark.usefixtures("db_session")
    def test_ok_if_user_offerer(self):
        user_offerer = offers_factories.UserOffererFactory()
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


class CheckApiKeyAllowsToValidateBookingTest:
    @pytest.mark.usefixtures("db_session")
    def test_does_not_raise_error_when_api_key_is_provided_and_is_related_to_offerer_id(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer, None)

        repository.save(offerer, user_offerer)

        validApiKey = ApiKey()
        validApiKey.prefix = "secret"
        validApiKey.offererId = offerer.id

        repository.save(validApiKey)

        # The the following should not raise
        check_api_key_allows_to_validate_booking(validApiKey, offerer.id)

    def test_raises_exception_when_api_key_is_provided_but_related_offerer_does_not_have_rights_on_booking(self, app):
        # Given
        validApiKey = ApiKey()
        validApiKey.prefix = "secret"
        validApiKey.offererId = 67

        # When
        with pytest.raises(ApiErrors) as errors:
            check_api_key_allows_to_validate_booking(validApiKey, None)

        # Then
        assert errors.value.errors["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]
