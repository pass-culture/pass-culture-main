from typing import Optional

from pcapi import settings
from pcapi.connectors import api_entreprises
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import Offerer
from pcapi.core.users.external import update_external_pro
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.bank_information import check_new_bank_information_has_a_more_advanced_status
from pcapi.domain.bank_information import check_new_bank_information_older_than_saved_one
from pcapi.domain.bank_information import check_offerer_presence
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.domain.bank_informations.bank_informations_repository import BankInformationsRepository
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.domain.demarches_simplifiees import get_venue_bank_information_application_details_by_application_id
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


PROCEDURE_ID_VERSION_MAP = {
    settings.DMS_VENUE_PROCEDURE_ID: 1,
    settings.DMS_VENUE_PROCEDURE_ID_V2: 2,
}


class SaveVenueBankInformations:
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        self.venue_repository = venue_repository
        self.bank_informations_repository = bank_informations_repository

    def execute(self, application_id: str, procedure_id: Optional[str] = None) -> Optional[BankInformations]:
        if not procedure_id:
            procedure_id = settings.DMS_VENUE_PROCEDURE_ID
        application_details = get_venue_bank_information_application_details_by_application_id(
            application_id, version=PROCEDURE_ID_VERSION_MAP[procedure_id]
        )

        try:
            siret = application_details.siret
            siren = application_details.siren
            offerer = Offerer.query.filter_by(siren=siren).one_or_none()
            check_offerer_presence(offerer)
            venue = self.get_referent_venue(application_details, offerer)
            business_unit = BusinessUnit.query.filter(BusinessUnit.siret == siret).one_or_none()
        except CannotRegisterBankInformation as error:
            if application_details.status == BankInformationStatus.ACCEPTED:
                raise error
            return None

        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)
        if not bank_information:
            bank_information = self.bank_informations_repository.find_by_venue(venue.identifier)

        if bank_information:
            check_new_bank_information_older_than_saved_one(bank_information, application_details.modification_date)
            if (
                bank_information.venue_id == venue.identifier
                and bank_information.application_id != application_details.application_id
            ):
                check_new_bank_information_has_a_more_advanced_status(bank_information, application_details.status)

        new_bank_informations = self.create_new_bank_informations(application_details, venue.identifier)

        if not bank_information:
            updated_bank_information = self.bank_informations_repository.save(new_bank_informations)
        elif bank_information.application_id == application_details.application_id:
            updated_bank_information = self.bank_informations_repository.update_by_application_id(new_bank_informations)
        elif bank_information.venue_id == venue.identifier:
            updated_bank_information = self.bank_informations_repository.update_by_venue_id(new_bank_informations)
        else:
            raise NotImplementedError()

        # TODO(xordoquy): remove the siret condition once the old DMS procedure is dropped
        if siret:
            if not business_unit:
                business_unit = BusinessUnit(
                    name=venue.publicName or venue.name,
                    siret=siret,
                    bankAccountId=updated_bank_information.id,
                )
            business_unit.bankAccountId = updated_bank_information.id
            repository.save(business_unit)
            offerers_api.set_business_unit_to_venue_id(business_unit.id, venue.identifier)

        update_external_pro(venue.bookingEmail)

        return bank_information

    def get_referent_venue(self, application_details: ApplicationDetail, offerer: Offerer) -> VenueWithBasicInformation:
        siret = application_details.siret

        if siret:
            venue = self.venue_repository.find_by_siret(siret)
            if not venue:
                raise CannotRegisterBankInformation("Venue not found")
            if not api_entreprises.check_siret_is_still_active(siret):
                raise CannotRegisterBankInformation("SIRET is no longer active")
        else:
            name = application_details.venue_name
            venues = self.venue_repository.find_by_name(name, offerer.id)
            if len(venues) == 0:
                raise CannotRegisterBankInformation("Venue name not found")
            if len(venues) > 1:
                raise CannotRegisterBankInformation("Multiple venues found")
            venue = venues[0]
        return venue

    def create_new_bank_informations(self, application_details: ApplicationDetail, venue_id: int) -> BankInformations:
        new_bank_informations = BankInformations()
        new_bank_informations.application_id = application_details.application_id
        new_bank_informations.venue_id = venue_id
        new_bank_informations.status = application_details.status
        new_bank_informations.date_modified = application_details.modification_date
        if application_details.status == BankInformationStatus.ACCEPTED:
            new_bank_informations.iban = application_details.iban
            new_bank_informations.bic = application_details.bic
        else:
            new_bank_informations.iban = None
            new_bank_informations.bic = None
        return new_bank_informations
