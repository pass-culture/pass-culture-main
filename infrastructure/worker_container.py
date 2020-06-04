from infrastructure.repository.offerer.offerer_sql_repository import OffererSQLRepository
from infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import VenueWithBasicInformationSQLRepository
from infrastructure.repository.bank_informations.bank_informations_sql_repository import BankInformationsSQLRepository
from use_cases.save_offerer_bank_informations import SaveOffererBankInformations
from use_cases.save_venue_bank_informations import SaveVenueBankInformations

# Repositories
offerer_repository = OffererSQLRepository()
bank_informations_repository = BankInformationsSQLRepository()
venue_identifier_repository = VenueWithBasicInformationSQLRepository()

# Usecases
save_offerer_bank_informations = SaveOffererBankInformations(offerer_repository=offerer_repository,
                                                             bank_informations_repository=bank_informations_repository
                                                             )

save_venue_bank_informations = SaveVenueBankInformations(offerer_repository=offerer_repository,
                                                         venue_repository=venue_identifier_repository,
                                                         bank_informations_repository=bank_informations_repository)
