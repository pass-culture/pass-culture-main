from pcapi.core.offerers.models import Offerer
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.bank_information import check_new_bank_information_has_a_more_advanced_status
from pcapi.domain.bank_information import check_new_bank_information_older_than_saved_one
from pcapi.domain.bank_information import check_offerer_presence
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.domain.bank_informations.bank_informations_repository import BankInformationsRepository
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.domain.demarches_simplifiees import get_offerer_bank_information_application_details_by_application_id
from pcapi.models.bank_information import BankInformationStatus


class SaveOffererBankInformations:
    def __init__(self, bank_informations_repository: BankInformationsRepository):
        self.bank_informations_repository = bank_informations_repository

    def execute(self, application_id: str):
        application_details = get_offerer_bank_information_application_details_by_application_id(application_id)

        try:
            offerer = Offerer.query.filter_by(siren=application_details.siren).one_or_none()
            check_offerer_presence(offerer)
        except CannotRegisterBankInformation as error:
            if application_details.status == BankInformationStatus.ACCEPTED:
                raise error
            return None

        bank_information_by_application_id = self.bank_informations_repository.get_by_application(
            application_details.application_id
        )

        if bank_information_by_application_id:
            check_new_bank_information_older_than_saved_one(
                bank_information_by_application_id, application_details.modification_date
            )
            new_bank_informations = self.create_new_bank_informations(application_details, offerer.id)
            return self.bank_informations_repository.update_by_application_id(new_bank_informations)

        bank_information_by_offerer_id = self.bank_informations_repository.find_by_offerer(offerer.id)

        if bank_information_by_offerer_id:
            check_new_bank_information_older_than_saved_one(
                bank_information_by_offerer_id, application_details.modification_date
            )
            check_new_bank_information_has_a_more_advanced_status(
                bank_information_by_offerer_id, application_details.status
            )

            new_bank_informations = self.create_new_bank_informations(application_details, offerer.id)
            return self.bank_informations_repository.update_by_offerer_id(new_bank_informations)

        new_bank_informations = self.create_new_bank_informations(application_details, offerer.id)
        return self.bank_informations_repository.save(new_bank_informations)

    def create_new_bank_informations(self, application_details: ApplicationDetail, offerer_id: str) -> BankInformations:
        new_bank_informations = BankInformations()
        new_bank_informations.application_id = application_details.application_id
        new_bank_informations.offerer_id = offerer_id
        new_bank_informations.status = application_details.status
        new_bank_informations.date_modified = application_details.modification_date
        if application_details.status == BankInformationStatus.ACCEPTED:
            new_bank_informations.iban = application_details.iban
            new_bank_informations.bic = application_details.bic
        else:
            new_bank_informations.iban = None
            new_bank_informations.bic = None
        return new_bank_informations
