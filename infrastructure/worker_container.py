from infrastructure.repository.offerer.offerer_sql_repository import OffererSQLRepository
from infrastructure.repository.venue.venue_sql_repository import VenueSQLRepository
from infrastructure.repository.bank_informations.bank_informations_sql_repository import BankInformationsSQLRepository
from use_cases.save_offerer_bank_informations import SaveOffererBankInformations
from use_cases.save_venue_bank_informations import SaveVenueBankInformations

# Repositories
offerer_repository = OffererSQLRepository()
bank_informations_repository = BankInformationsSQLRepository()
venue_repository = VenueSQLRepository()

# Usecases
save_offerer_bank_informations = SaveOffererBankInformations(offerer_repository=offerer_repository,
                                                             bank_informations_repository=bank_informations_repository
                                                             )

save_venue_bank_informations = SaveVenueBankInformations(offerer_repository=offerer_repository,
                                                         venue_repository=venue_repository,
                                                         bank_informations_repository=bank_informations_repository)
