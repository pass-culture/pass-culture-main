from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.use_cases.save_offerer_bank_informations import SaveOffererBankInformations
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformations


# Repositories
bank_informations_repository = BankInformationsSQLRepository()
venue_identifier_repository = VenueWithBasicInformationSQLRepository()

# Usecases
save_offerer_bank_informations = SaveOffererBankInformations(bank_informations_repository=bank_informations_repository)

save_venue_bank_informations = SaveVenueBankInformations(
    venue_repository=venue_identifier_repository,
    bank_informations_repository=bank_informations_repository,
)
