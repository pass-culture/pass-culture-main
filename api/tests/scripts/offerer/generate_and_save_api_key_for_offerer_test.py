import pytest

from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import ApiKey
import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.offerer.generate_and_save_api_key_for_offerer import generate_and_save_api_key_for_offerer


@pytest.mark.usefixtures("db_session")
def test_generate_and_save_api_key_for_offerer():
    # Given
    siren_unknown = "291893841948"
    offerer_1_having_api_key = offers_factories.OffererFactory()
    ApiKeyFactory(offerer=offerer_1_having_api_key)

    offerer_2_needing_api_key = offers_factories.OffererFactory()

    # When
    generate_and_save_api_key_for_offerer(
        [siren_unknown, offerer_1_having_api_key.siren, offerer_2_needing_api_key.siren]
    )

    # Then
    assert ApiKey.query.count() == 2
    offerers = {k.offerer for k in ApiKey.query.all()}
    assert offerers == {offerer_1_having_api_key, offerer_2_needing_api_key}
