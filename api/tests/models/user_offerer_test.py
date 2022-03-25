import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_save_user_offerer_raise_api_error_when_not_unique(app):
    user = users_factories.ProFactory.build()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=user, offerer=offerer)

    uo2 = offerers_factories.UserOffererFactory.build(user=user, offerer=offerer)
    with pytest.raises(ApiErrors) as error:
        repository.save(uo2)

    assert error.value.errors["global"] == ["Une entrée avec cet identifiant existe déjà dans notre base de données"]
