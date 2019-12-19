import pytest

from tests.conftest import clean_database
from models import ApiErrors, ApiKey, PcObject
from utils.token import random_token

from tests.model_creators.generic_creators import create_offerer


@clean_database
def test_save_api_key_raise_api_error_when_offerer_does_not_exist(app):
    # given
    offererApiKey = ApiKey()
    offererApiKey.value = random_token(64)
    offererApiKey.offererId = 65675

    # when
    with pytest.raises(ApiErrors) as error:
        PcObject.save(offererApiKey)

    # then
    assert error.value.errors['offererId'] == ['Aucun objet ne correspond à cet identifiant dans notre base de données']

@clean_database
def test_save_api_key_create_relation_offerer_api_key(app):
    # given(
    offerer = create_offerer()
    PcObject.save(offerer)

    offererApiKey = ApiKey()
    offererApiKey.value = random_token(64)
    offererApiKey.offererId = offerer.id

    # when
    PcObject.save(offererApiKey)

    # then
    assert offerer.apiKey.value == offererApiKey.value
