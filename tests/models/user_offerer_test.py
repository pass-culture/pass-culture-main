import pytest

from models import ApiErrors
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer


@clean_database
def test_save_user_offerer_raise_api_error_when_not_unique(app):
    # Given
    user = create_user()
    offerer = create_offerer()
    uo1 = create_user_offerer(user, offerer)
    repository.save(user, offerer, uo1)
    uo2 = create_user_offerer(user, offerer)

    # When
    with pytest.raises(ApiErrors) as error:
        repository.save(uo2)

    assert error.value.errors["global"] == ['Une entrée avec cet identifiant existe déjà dans notre base de données']
