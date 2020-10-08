from pcapi.infrastructure.repository.beneficiary.beneficiary_jouve_repository import BeneficiaryJouveRepository
from pcapi.infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from pcapi.infrastructure.repository.offerer.offerer_sql_repository import OffererSQLRepository
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import VenueWithBasicInformationSQLRepository
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import BankInformationsSQLRepository
from pcapi.use_cases.create_beneficiary_from_application import CreateBeneficiaryFromApplication
from pcapi.use_cases.save_offerer_bank_informations import SaveOffererBankInformations
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformations

# Repositories
beneficiary_pre_subscription_repository = BeneficiaryJouveRepository()
bank_informations_repository = BankInformationsSQLRepository()
offerer_repository = OffererSQLRepository()
beneficiary_repository = BeneficiarySQLRepository()
venue_identifier_repository = VenueWithBasicInformationSQLRepository()

# Usecases
create_beneficiary_from_application = CreateBeneficiaryFromApplication(
    beneficiary_pre_subscription_repository=beneficiary_pre_subscription_repository,
    beneficiary_repository=beneficiary_repository
)

save_offerer_bank_informations = SaveOffererBankInformations(offerer_repository=offerer_repository,
                                                             bank_informations_repository=bank_informations_repository
                                                             )

save_venue_bank_informations = SaveVenueBankInformations(offerer_repository=offerer_repository,
                                                         venue_repository=venue_identifier_repository,
                                                         bank_informations_repository=bank_informations_repository)
