from abc import ABC
import logging
import typing

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.connectors.dms.serializer import ApplicationDetailOldJourney
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.bank_information import check_new_bank_information_has_a_more_advanced_status
from pcapi.domain.bank_information import check_new_bank_information_older_than_saved_one
from pcapi.domain.bank_information import check_new_bank_information_valid
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.domain.bank_informations.bank_informations_repository import BankInformationsRepository
from pcapi.domain.demarches_simplifiees import archive_dossier
from pcapi.domain.demarches_simplifiees import format_error_to_demarches_simplifiees_text
from pcapi.domain.demarches_simplifiees import update_demarches_simplifiees_text_annotations
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.models.api_errors import ApiErrors
from pcapi.utils import urls


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Venue


logger = logging.getLogger(__name__)

PROCEDURE_ID_VERSION_MAP = {
    settings.DMS_VENUE_PROCEDURE_ID_V2: 2,
    settings.DMS_VENUE_PROCEDURE_ID_V3: 3,
    settings.DMS_VENUE_PROCEDURE_ID_V4: 4,
    settings.DS_BANK_ACCOUNT_PROCEDURE_ID: 5,
}


class AbstractSaveBankInformations(ABC):
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        self.venue_repository = venue_repository
        self.bank_informations_repository = bank_informations_repository
        self.api_errors = CannotRegisterBankInformation()
        self.procedure_version: int

    def execute(self, application_details: ApplicationDetailOldJourney) -> BankInformations | None:
        raise NotImplementedError()

    def get_referent_venue(
        self,
        application_details: ApplicationDetailOldJourney,
    ) -> VenueWithBasicInformation | None:
        raise NotImplementedError()


class SaveVenueBankInformationsMixin(AbstractSaveBankInformations):
    def create_new_bank_informations(
        self,
        application_details: ApplicationDetailOldJourney,
        venue_id: int | None = None,
        offerer_id: int | None = None,
    ) -> BankInformations:
        new_bank_informations = BankInformations()
        new_bank_informations.application_id = application_details.application_id
        new_bank_informations.venue_id = venue_id
        new_bank_informations.offerer_id = offerer_id
        new_bank_informations.status = application_details.status
        new_bank_informations.date_modified = application_details.modification_date
        if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
            new_bank_informations.iban = application_details.iban
            new_bank_informations.bic = application_details.bic
        else:
            new_bank_informations.iban = None
            new_bank_informations.bic = None
        return new_bank_informations


class SaveVenueBankInformationsV2(SaveVenueBankInformationsMixin):
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        super().__init__(venue_repository=venue_repository, bank_informations_repository=bank_informations_repository)
        self.procedure_version = 2

    def execute(self, application_details: ApplicationDetailOldJourney) -> BankInformations | None:
        logger.info(
            "This DMS application was created on a bank info procedure that is deprecated.",
            extra={
                "application_id": application_details.application_id,
                "procedure_version": self.procedure_version,
            },
        )

        venue = self.get_referent_venue(application_details)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                if application_details.status != finance_models.BankInformationStatus.REJECTED:
                    update_demarches_simplifiees_text_annotations(
                        application_details.dossier_id,
                        application_details.error_annotation_id,
                        format_error_to_demarches_simplifiees_text(self.api_errors),
                    )
                return None
            if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
                raise self.api_errors
            return None

        assert venue  # for typing purposes
        venue_sql_entity = offerers_models.Venue.query.get(venue.identifier)

        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)
        if not bank_information:
            bank_information = self.bank_informations_repository.find_by_venue(venue.identifier)

        if bank_information:
            check_new_bank_information_older_than_saved_one(
                bank_information, application_details.modification_date, self.api_errors
            )
            if (
                bank_information.venue_id == venue.identifier
                and bank_information.application_id != application_details.application_id
            ):
                check_new_bank_information_has_a_more_advanced_status(
                    bank_information, application_details.status, self.api_errors
                )

        new_bank_informations = self.create_new_bank_informations(application_details, venue.identifier)

        check_new_bank_information_valid(new_bank_informations, self.api_errors)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    format_error_to_demarches_simplifiees_text(self.api_errors),
                )
                return None
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                return None
            raise self.api_errors

        if not bank_information:
            self.bank_informations_repository.save(new_bank_informations)
        elif bank_information.application_id == application_details.application_id:
            self.bank_informations_repository.update_by_application_id(new_bank_informations)
        elif bank_information.venue_id == venue.identifier:
            self.bank_informations_repository.update_by_venue_id(new_bank_informations)
        else:
            raise NotImplementedError()

        if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
            try:
                offerers_api.link_venue_to_reimbursement_point(venue_sql_entity, venue.identifier)
            except ApiErrors as exc:
                logger.error(
                    "Could not link venue to itself as its reimbursement point with legacy DMS procedure",
                    extra={
                        "procedure_version": self.procedure_version,
                        "application_id": application_details.application_id,
                        "err": exc.errors,
                        "venue": venue_sql_entity.id,
                    },
                )

        update_external_pro(venue.bookingEmail)
        if application_details.error_annotation_id is not None:
            if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Dossier successfully imported",
                )
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Valid dossier",
                )
        if application_details.status != finance_models.BankInformationStatus.DRAFT:
            archive_dossier(application_details.dossier_id)
        return bank_information

    # TODO(fseguin, 2022-07-11): clean up when previous procedures are retired
    def get_referent_venue(
        self,
        application_details: ApplicationDetailOldJourney,
    ) -> VenueWithBasicInformation | None:
        venue = None

        siret = (application_details.siret or "").strip()
        if siret:
            venue = self.venue_repository.find_by_siret(siret)
        if not venue:
            self.api_errors.add_error("Venue", "Venue not found")
        else:
            try:
                if not sirene.siret_is_active(siret):
                    self.api_errors.add_error("Venue", "SIRET is no longer active")
            except sirene.SireneException:
                self.api_errors.add_error("Venue", "Error while checking SIRET on Sirene API")

        assert venue or self.api_errors.errors
        return venue


class SaveVenueBankInformationsV3(SaveVenueBankInformationsV2):
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        super().__init__(venue_repository=venue_repository, bank_informations_repository=bank_informations_repository)
        self.procedure_version = 3


class SaveVenueBankInformationsV4(SaveVenueBankInformationsMixin):
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        super().__init__(venue_repository=venue_repository, bank_informations_repository=bank_informations_repository)
        self.procedure_version = 4

    def execute(self, application_details: ApplicationDetailOldJourney) -> BankInformations | None:
        venue = self.get_referent_venue(application_details)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                if application_details.status != finance_models.BankInformationStatus.REJECTED:
                    update_demarches_simplifiees_text_annotations(
                        application_details.dossier_id,
                        application_details.error_annotation_id,
                        format_error_to_demarches_simplifiees_text(self.api_errors),
                    )
                return None
            if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
                raise self.api_errors
            return None

        assert venue  # for typing purposes
        venue_sql_entity = offerers_models.Venue.query.get(venue.identifier)

        self.fill_venue_url_application_field(application_details=application_details, venue=venue_sql_entity)

        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)
        if not bank_information:
            bank_information = self.bank_informations_repository.find_by_venue(venue.identifier)

        if bank_information:
            check_new_bank_information_older_than_saved_one(
                bank_information, application_details.modification_date, self.api_errors
            )
            if (
                bank_information.venue_id == venue.identifier
                and bank_information.application_id != application_details.application_id
            ):
                check_new_bank_information_has_a_more_advanced_status(
                    bank_information, application_details.status, self.api_errors
                )

        new_bank_informations = self.create_new_bank_informations(application_details, venue.identifier)

        check_new_bank_information_valid(new_bank_informations, self.api_errors)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    format_error_to_demarches_simplifiees_text(self.api_errors),
                )
                return None
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                return None
            raise self.api_errors

        if not bank_information:
            self.bank_informations_repository.save(new_bank_informations)
        elif bank_information.application_id == application_details.application_id:
            self.bank_informations_repository.update_by_application_id(new_bank_informations)
        elif bank_information.venue_id == venue.identifier:
            self.bank_informations_repository.update_by_venue_id(new_bank_informations)
        else:
            raise NotImplementedError()

        if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
            offerers_api.link_venue_to_reimbursement_point(venue_sql_entity, venue.identifier)

        update_external_pro(venue.bookingEmail)
        if application_details.error_annotation_id is not None:
            if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Dossier successfully imported",
                )
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Valid dossier",
                )
        if application_details.status != finance_models.BankInformationStatus.DRAFT:
            archive_dossier(application_details.dossier_id)
        return bank_information

    # TODO(fseguin, 2022-07-11): clean up when previous procedures are retired
    def get_referent_venue(
        self,
        application_details: ApplicationDetailOldJourney,
    ) -> VenueWithBasicInformation | None:
        venue = None

        dms_token = (application_details.dms_token or "").strip()
        if dms_token:
            venue = self.venue_repository.find_by_dms_token(dms_token)
        if not venue:
            self.api_errors.add_error("Venue", "Venue not found")

        assert venue or self.api_errors.errors
        return venue

    def fill_venue_url_application_field(
        self, application_details: ApplicationDetailOldJourney, venue: "Venue"
    ) -> None:
        if application_details.venue_url_annotation_id is None:
            logger.error("venue_url_annotation_id cannot be None in DSv4 context")
            return

        update_demarches_simplifiees_text_annotations(
            application_details.dossier_id,
            application_details.venue_url_annotation_id,
            urls.build_pc_pro_venue_link(venue),
        )


class SaveVenueBankInformationsV5(SaveVenueBankInformationsMixin):
    def __init__(
        self,
        venue_repository: VenueWithBasicInformationRepository,
        bank_informations_repository: BankInformationsRepository,
    ):
        super().__init__(venue_repository=venue_repository, bank_informations_repository=bank_informations_repository)
        self.procedure_version = 5

    def execute(self, application_details: ApplicationDetailOldJourney) -> BankInformations | None:
        venue = self.get_referent_venue(application_details)

        if venue is None:
            # None or more than one venue, we can’t know what to do
            # Creating bank information and returning earlier
            assert application_details.siret  # helps mypy
            siren = application_details.siret[:9]
            offerer_id, *_ = (
                offerers_models.Offerer.query.filter_by(siren=siren)
                .with_entities(offerers_models.Offerer.id)
                .one_or_none()
            )
            if offerer_id is None:
                logger.error("Can't find an offerer by siren: %s", siren)
                return None
            newly_bank_information = self.create_new_bank_informations(application_details, offerer_id=offerer_id)
            self.bank_informations_repository.save(newly_bank_information)
            return None

        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)

        if bank_information:
            check_new_bank_information_older_than_saved_one(
                bank_information, application_details.modification_date, self.api_errors
            )
            if (
                bank_information.venue_id == venue.id
                and bank_information.application_id != application_details.application_id
            ):
                check_new_bank_information_has_a_more_advanced_status(
                    bank_information, application_details.status, self.api_errors
                )

        new_bank_informations = self.create_new_bank_informations(application_details, venue.id)

        check_new_bank_information_valid(new_bank_informations, self.api_errors)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    format_error_to_demarches_simplifiees_text(self.api_errors),
                )
                return None
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                return None
            raise self.api_errors

        if not bank_information:
            self.bank_informations_repository.save(new_bank_informations)
        elif bank_information.application_id == application_details.application_id:
            self.bank_informations_repository.update_by_application_id(new_bank_informations)
        elif bank_information.venue_id == venue.id:
            self.bank_informations_repository.update_by_venue_id(new_bank_informations)
        else:
            raise NotImplementedError()

        if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
            offerers_api.link_venue_to_reimbursement_point(venue, venue.id)

        update_external_pro(venue.bookingEmail)
        if application_details.error_annotation_id is not None:
            if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Dossier successfully imported",
                )
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                update_demarches_simplifiees_text_annotations(
                    application_details.dossier_id,
                    application_details.error_annotation_id,
                    "Valid dossier",
                )
        if application_details.status != finance_models.BankInformationStatus.DRAFT:
            archive_dossier(application_details.dossier_id)
        return bank_information

    def get_referent_venue(
        self,
        application_details: ApplicationDetailOldJourney,
    ) -> "Venue | None":
        """
        Return a Venue only if one exists, otherwise return None.
        We only need the Venue to linked it to a bank account.
        If there are many (or None), we can’t do anything
        (because we can’t know to which Venue the user might
        want to link this bank account.)
        """
        if application_details.siret is None:
            logger.error("siret cannot be None at this point in the DSv5 context.")
            return None
        _, venues = offerers_repository.find_venues_of_offerer_from_siret(application_details.siret)
        if not venues or len(venues) > 1:
            logger.warning(
                "Can't link a BankInformation to a venue",
                extra={
                    "siren": application_details.siret,
                    "application_id": application_details.application_id,
                    "has_venues": bool(venues),
                },
            )
            return None
        return venues[0]


class SaveVenueBankInformationsFactory:
    procedure_to_class = {
        2: SaveVenueBankInformationsV2,
        3: SaveVenueBankInformationsV3,
        4: SaveVenueBankInformationsV4,
        5: SaveVenueBankInformationsV5,
    }

    @classmethod
    def get(cls, procedure_id: str) -> "type[AbstractSaveBankInformations]":
        return cls.procedure_to_class[PROCEDURE_ID_VERSION_MAP[procedure_id]]
