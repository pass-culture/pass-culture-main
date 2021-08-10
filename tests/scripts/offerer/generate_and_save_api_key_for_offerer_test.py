import logging

import pytest

from pcapi.core.offerers.factories import ApiKeyFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.offerer.generate_and_save_api_key_for_offerer import generate_and_save_api_key_for_offerer


@pytest.mark.usefixtures("db_session")
def test_generate_and_save_api_key_for_offerer(caplog):
    # Given
    caplog.set_level(logging.INFO)
    siren_unknown = "291893841948"
    offerer_1_having_api_key = offers_factories.OffererFactory()
    ApiKeyFactory(offerer=offerer_1_having_api_key)

    offerer_2_needing_api_key = offers_factories.OffererFactory()

    # When
    logging_lines = generate_and_save_api_key_for_offerer(
        [siren_unknown, offerer_1_having_api_key.siren, offerer_2_needing_api_key.siren]
    )

    # Then
    assert caplog.record_tuples[0][0] == "pcapi.scripts.offerer.generate_and_save_api_key_for_offerer"
    assert caplog.record_tuples[0][1] == logging.INFO
    assert logging_lines[0][0] == siren_unknown
    assert logging_lines[0][1] == "X"
    assert logging_lines[0][2] == "Error: Siren inconnu"

    assert logging_lines[1][0] == offerer_1_having_api_key.siren
    assert logging_lines[1][1] == "X"
    assert logging_lines[1][2] == "Warning: Clé déjà existante pour ce siren"

    assert logging_lines[2][0] == offerer_2_needing_api_key.siren
    assert logging_lines[2][1] != "X"
    assert logging_lines[2][2] == "Success"
