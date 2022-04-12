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
from pcapi.domain.bank_information import check_new_bank_information_valid
from pcapi.domain.bank_information import check_offerer_presence
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.domain.bank_informations.bank_informations_repository import BankInformationsRepository
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.domain.demarches_simplifiees import format_error_to_demarches_simplifiees_text
from pcapi.domain.demarches_simplifiees import get_venue_bank_information_application_details_by_application_id
from pcapi.domain.demarches_simplifiees import update_demarches_simplifiees_text_annotations
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


PROCEDURE_ID_VERSION_MAP = {
    settings.DMS_VENUE_PROCEDURE_ID: 1,
    settings.DMS_VENUE_PROCEDURE_ID_V2: 2,
    settings.DMS_VENUE_PROCEDURE_ID_V3: 2,
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

        api_errors = CannotRegisterBankInformation()
        siret = application_details.siret
        siren = application_details.siren
        offerer = Offerer.query.filter_by(siren=siren).one_or_none()
        check_offerer_presence(offerer, api_errors)
        venue = self.get_referent_venue(application_details, offerer, api_errors)
        business_unit = BusinessUnit.query.filter(BusinessUnit.siret == siret).one_or_none()

        if api_errors.errors:
            if application_details.annotation_id is not None:
                if application_details.status != BankInformationStatus.REJECTED:
                    update_demarches_simplifiees_text_annotations(
                        application_details.dossier_id,  # type: ignore [arg-type]
                        application_details.annotation_id,
                        format_error_to_demarches_simplifiees_text(api_errors),
                    )
                return None
            if application_details.status == BankInformationStatus.ACCEPTED:
                raise api_errors
            return None

        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)
        if not bank_information:
            bank_information = self.bank_informations_repository.find_by_venue(venue.identifier)

        if bank_information:
            check_new_bank_information_older_than_saved_one(
                bank_information, application_details.modification_date, api_errors
            )
            if (
                bank_information.venue_id == venue.identifier
                and bank_information.application_id != application_details.application_id
            ):
                check_new_bank_information_has_a_more_advanced_status(
                    bank_information, application_details.status, api_errors
                )

        new_bank_informations = self.create_new_bank_informations(application_details, venue.identifier)

        check_new_bank_information_valid(new_bank_informations, api_errors)

        if api_errors.errors:
            if application_details.annotation_id is not None:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,  # type: ignore [arg-type]
                    application_details.annotation_id,
                    format_error_to_demarches_simplifiees_text(api_errors),
                )
                return None
            raise api_errors

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
        if application_details.annotation_id is not None:
            if application_details.status == BankInformationStatus.ACCEPTED:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id, application_details.annotation_id, "Dossier imported Sucessfully"
                )
        return bank_information

    def get_referent_venue(
        self, application_details: ApplicationDetail, offerer: Offerer, api_errors: CannotRegisterBankInformation
    ) -> VenueWithBasicInformation:
        siret = application_details.siret
        if siret:
            venue = self.venue_repository.find_by_siret(siret)
            if not venue:
                api_errors.add_error("Venue", "Venue not found")
            try:
                is_siret_active = api_entreprises.check_siret_is_still_active(siret)
                if not is_siret_active:
                    api_errors.add_error("Venue", "SIRET is no longer active")
            except api_entreprises.ApiEntrepriseException:
                api_errors.add_error("Venue", "Error while checking SIRET on Api Entreprise")

        else:
            if not offerer:
                return None  # type: ignore [return-value]
            name = application_details.venue_name
            venues = self.venue_repository.find_by_name(name, offerer.id)  # type: ignore [arg-type]
            if len(venues) == 0:
                api_errors.add_error("Venue", "Venue name not found")
            if len(venues) > 1:
                api_errors.add_error("Venue", "Multiple venues found")
            if api_errors.errors:
                return None  # type: ignore [return-value]
            venue = venues[0]
        return venue

    def create_new_bank_informations(self, application_details: ApplicationDetail, venue_id: int) -> BankInformations:
        new_bank_informations = BankInformations()
        new_bank_informations.application_id = application_details.application_id  # type: ignore [assignment]
        new_bank_informations.venue_id = venue_id
        new_bank_informations.status = application_details.status  # type: ignore [assignment]
        new_bank_informations.date_modified = application_details.modification_date
        if application_details.status == BankInformationStatus.ACCEPTED:
            new_bank_informations.iban = application_details.iban
            new_bank_informations.bic = application_details.bic
        else:
            new_bank_informations.iban = None
            new_bank_informations.bic = None
        return new_bank_informations
