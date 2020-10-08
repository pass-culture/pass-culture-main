import pytest

from models import ApiErrors, ApiKey
from repository import repository
import pytest
from model_creators.generic_creators import create_offerer
from utils.token import random_token


@pytest.mark.usefixtures("db_session")
def test_save_api_key_raise_api_error_when_offerer_does_not_exist(app):
    # given
    offererApiKey = ApiKey()
    offererApiKey.value = random_token(64)
    offererApiKey.offererId = 65675

    # when
    with pytest.raises(ApiErrors) as error:
        repository.save(offererApiKey)

    # then
    assert error.value.errors['offererId'] == ['Aucun objet ne correspond à cet identifiant dans notre base de données']

@pytest.mark.usefixtures("db_session")
def test_save_api_key_create_relation_offerer_api_key(app):
    # given(
    offerer = create_offerer()
    repository.save(offerer)

    offererApiKey = ApiKey()
    offererApiKey.value = random_token(64)
    offererApiKey.offererId = offerer.id

    # when
    repository.save(offererApiKey)

    # then
    assert offerer.apiKey.value == offererApiKey.value
