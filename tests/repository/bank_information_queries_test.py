from datetime import datetime

from repository import repository
from repository.bank_information_queries import get_last_update_from_bank_information
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information, create_provider


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
        repository.save(bank_information)

        # when
        last_update = get_last_update_from_bank_information()

        # then
        assert last_update == datetime(2019, 1, 1)

    @clean_database
    def when_bank_information_table_records_has_different_provider_ids_return_correct_date(self, app):
        # given
        provider = create_provider(idx=1, local_class='TestLocalProvider')
        other_provider = create_provider(
            idx=2, local_class='TestLocalProviderWithThumb')
        repository.save(provider, other_provider)

        offerer = create_offerer(siren='793875019')
        venue = create_venue(offerer, siret='79387501900056')
        other_venue = create_venue(offerer, siret='79387501900058')

        target_date = datetime(2019, 1, 1)
        recent_date = datetime(2020, 1, 1)

        bank_information = create_bank_information(id_at_providers='79387501900056',
                                                   date_modified_at_last_provider=target_date,
                                                   venue=venue,
                                                   last_provider_id=provider.id,
                                                   application_id=1)
        other_bank_information = create_bank_information(id_at_providers='79387501900058',
                                                         date_modified_at_last_provider=recent_date,
                                                         venue=other_venue,
                                                         last_provider_id=other_provider.id,
                                                         application_id=2)
        repository.save(bank_information, other_bank_information)

        # when
        last_update = get_last_update_from_bank_information(
            last_provider_id=provider.id)

        # then
        assert last_update == target_date
