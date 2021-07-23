import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.models import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_save_user_offerer_raise_api_error_when_not_unique(app):
    # Given
    user = users_factories.UserFactory.build()
    offerer = create_offerer()
    uo1 = create_user_offerer(user, offerer)
    repository.save(user, offerer, uo1)
    uo2 = create_user_offerer(user, offerer)

    # When
    with pytest.raises(ApiErrors) as error:
        repository.save(uo2)

    assert error.value.errors["global"] == ["Une entrée avec cet identifiant existe déjà dans notre base de données"]
