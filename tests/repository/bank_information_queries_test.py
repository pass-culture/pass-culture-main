from datetime import datetime

from models import PcObject
from repository.bank_information_queries import get_last_update_from_bank_information
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information


class GetLastUpdateForBankInformationTest:
    @clean_database
    def when_bank_information_table_is_empty_returns_1900_01_01(self, app):
        # when
        last_update = get_last_update_from_bank_information()

        # then
        assert last_update == datetime(1900, 1, 1)

    @clean_database
    def when_bank_information_table_has_max_update_2019_1_1_returns_2019_1_1(self, app):
        # given
        offerer = create_offerer(siren='793875019')
        venue = create_venue(offerer, siret='79387501900056')

        bank_information = create_bank_information(id_at_providers='79387501900056',
                                                   date_modified_at_last_provider=datetime(2019, 1, 1), venue=venue)
        PcObject.save(bank_information)

        # when
        last_update = get_last_update_from_bank_information()

        # then
        assert last_update == datetime(2019, 1, 1)
