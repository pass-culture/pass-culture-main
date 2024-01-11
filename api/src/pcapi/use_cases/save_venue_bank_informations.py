from abc import ABC
from datetime import datetime
import logging
import typing

import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm

from pcapi import settings
from pcapi.connectors.dms.serializer import ApplicationDetailNewJourney
from pcapi.connectors.dms.serializer import ApplicationDetailOldJourney
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
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
from pcapi.models import db
from pcapi.utils import urls


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Venue, Offerer

from pcapi.utils.db import make_timerange


logger = logging.getLogger(__name__)

PROCEDURE_ID_VERSION_MAP = {
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
    def get_or_create_new_bank_informations(
        self,
        application_details: ApplicationDetailOldJourney,
        venue_id: int | None = None,
        offerer_id: int | None = None,
    ) -> BankInformations:
        bank_information = self.bank_informations_repository.get_by_application(application_details.application_id)
        if not bank_information:
            bank_information = BankInformations()

        bank_information.application_id = application_details.application_id
        bank_information.venue_id = venue_id
        bank_information.offerer_id = offerer_id
        bank_information.status = application_details.status
        bank_information.date_modified = application_details.modification_date
        if application_details.status == finance_models.BankInformationStatus.ACCEPTED:
            bank_information.iban = application_details.iban
            bank_information.bic = application_details.bic
        else:
            bank_information.iban = None
            bank_information.bic = None
        return bank_information

    def annotate_application(self, application_detail: ApplicationDetailOldJourney, message: str) -> None:
        """
        Annotate the application with the rightfull message at the end of the automated process.
        Prepend if private annotation already exists
        """
        if application_detail.error_annotation_value:
            if message in application_detail.error_annotation_value:
                return
            message = f"{message}, {application_detail.error_annotation_value}"

        update_demarches_simplifiees_text_annotations(
            dossier_id=application_detail.dossier_id,
            annotation_id=application_detail.error_annotation_id,
            message=message,
        )

    def annotate_application_with_errors(self, application_detail: ApplicationDetailOldJourney) -> None:
        """
        Annotate the application with errors raised while processing it.
        Prepend if private annotation already exists
        """
        message = format_error_to_demarches_simplifiees_text(self.api_errors)
        if application_detail.error_annotation_value:
            if message in application_detail.error_annotation_value:
                return
            message = f"{message}, {application_detail.error_annotation_value}"

        update_demarches_simplifiees_text_annotations(
            dossier_id=application_detail.dossier_id,
            annotation_id=application_detail.error_annotation_id,
            message=message,
        )


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
                    self.annotate_application_with_errors(application_detail=application_details)
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

        new_bank_informations = self.get_or_create_new_bank_informations(application_details, venue.identifier)

        check_new_bank_information_valid(new_bank_informations, self.api_errors)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                self.annotate_application_with_errors(application_detail=application_details)
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
                self.annotate_application(
                    application_detail=application_details, message="Dossier successfully imported"
                )
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                self.annotate_application(application_detail=application_details, message="Valid dossier")
        if application_details.status != finance_models.BankInformationStatus.DRAFT:
            archive_dossier(application_details.dossier_id)
        return bank_information

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
        venue_link = urls.build_pc_pro_venue_link(venue)

        if application_details.venue_url_annotation_value == venue_link:
            logger.info("venue link annotation already filled")
            return

        update_demarches_simplifiees_text_annotations(
            application_details.dossier_id,
            application_details.venue_url_annotation_id,
            venue_link,
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
        if application_details.siret is None:
            logger.info(
                "siret cannot be None at this point in the DSv5 context.",
                extra={"application_id": application_details.application_id},
            )
            return None

        venue = self.get_referent_venue(application_details)

        if not venue:
            offerer_id = self.get_offerer_id(application_details)
            if not offerer_id:
                logger.info("Can't find an offerer by siret: %s", extra={"siret": application_details.siret})
                return None
            newly_bank_information = self.get_or_create_new_bank_informations(
                application_details, offerer_id=offerer_id
            )
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

        new_bank_informations = self.get_or_create_new_bank_informations(application_details, venue.id)

        check_new_bank_information_valid(new_bank_informations, self.api_errors)

        if self.api_errors.errors:
            if application_details.error_annotation_id is not None:
                self.annotate_application_with_errors(application_detail=application_details)
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
                self.annotate_application(
                    application_detail=application_details, message="Dossier successfully imported"
                )
            if application_details.status == finance_models.BankInformationStatus.DRAFT:
                self.annotate_application(application_detail=application_details, message="Valid dossier")
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
        assert application_details.siret  # helps mypy
        venues = (
            offerers_models.Venue.query.join(offerers_models.Venue.managingOfferer)
            .filter(
                offerers_models.Offerer.siren == application_details.siret[:9], offerers_models.Venue.isVirtual == False
            )
            .all()
        )
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

    def get_offerer_id(self, application_details: ApplicationDetailOldJourney) -> int | None:
        assert application_details.siret  # helps mypy
        offerer_id = (
            offerers_models.Offerer.query.filter_by(siren=application_details.siret[:9])
            .with_entities(offerers_models.Offerer.id)
            .one_or_none()
        )
        if offerer_id:
            return offerer_id[0]
        return None


class SaveVenueBankInformationsFactory:
    procedure_to_class = {
        4: SaveVenueBankInformationsV4,
        5: SaveVenueBankInformationsV5,
    }

    @classmethod
    def get(cls, procedure_id: str) -> "type[AbstractSaveBankInformations]":
        return cls.procedure_to_class[PROCEDURE_ID_VERSION_MAP[procedure_id]]


### New BankAccount Journey ###


class AbstractImportBankAccount:
    def __init__(self, application_details: ApplicationDetailNewJourney) -> None:
        self.application_details = application_details

    def execute(self) -> None:
        raise NotImplementedError()

    def get_venue(self) -> "Venue | None":
        raise NotImplementedError()


class ImportBankAccountMixin:
    # Let mypy know this class is going to be mixed with a child of `AbstractImportBankAccount`
    application_details: ApplicationDetailNewJourney

    def get_or_create_bank_account(
        self,
        offerer: offerers_models.Offerer,
        venue: "Venue | None" = None,
    ) -> finance_models.BankAccount:
        """
        Retrieve a bankAccount if already existing and update the status
        or create it and fill it with DS metadata.
        """
        bank_account = (
            finance_models.BankAccount.query.filter_by(dsApplicationId=self.application_details.application_id)
            .options(sqla_orm.load_only(finance_models.BankAccount.id))
            .join(
                finance_models.BankAccountStatusHistory,
                sqla.and_(
                    finance_models.BankAccountStatusHistory.bankAccountId == finance_models.BankAccount.id,
                    finance_models.BankAccountStatusHistory.timespan.contains(datetime.utcnow()),
                ),
            )
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sqla.and_(
                    offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                ),
            )
            .outerjoin(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
            .options(sqla_orm.contains_eager(finance_models.BankAccount.statusHistory))
            .options(
                sqla_orm.contains_eager(finance_models.BankAccount.venueLinks)
                .contains_eager(offerers_models.VenueBankAccountLink.venue)
                .load_only(offerers_models.Venue.id)
            )
            .one_or_none()
        )
        if bank_account is None:
            label = self.application_details.label
            if label is None:
                label = venue.common_name if venue is not None else self.application_details.obfuscatedIban
            bank_account = finance_models.BankAccount(
                iban=self.application_details.iban,
                bic=self.application_details.bic,
                label=label,
                offerer=offerer,
                dsApplicationId=self.application_details.application_id,
            )
        bank_account.status = self.application_details.status
        db.session.add(bank_account)
        return bank_account

    def link_venue_to_bank_account(
        self, bank_account: finance_models.BankAccount, venue: "Venue"
    ) -> offerers_models.VenueBankAccountLink | None:
        """
        Link a venue to a bankAccount only if it was accepted by the compliance.
        Do nothing if the link is already up to date.
        (The bankAccount might have been fetched because of a status update but already processed before)
        """
        if bank_account.status != BankAccountApplicationStatus.ACCEPTED:
            return None

        if bank_account.venueLinks:
            current_link = bank_account.current_link
            assert current_link  # helps mypy
            if current_link.venue == venue:
                logger.info(
                    "bank_account already linked to its venue",
                    extra={
                        "application_id": self.application_details.application_id,
                        "bank_account_id": bank_account.id,
                        "venue_id": venue.id,
                    },
                )
                return None

        if venue.bankAccountLinks:
            deprecated_link = venue.bankAccountLinks[0]
            lower_bound = deprecated_link.timespan.lower
            upper_bound = datetime.utcnow()
            timespan = make_timerange(start=lower_bound, end=upper_bound)
            deprecated_link.timespan = timespan
            deprecated_log = history_models.ActionHistory(
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                venueId=venue.id,
                bankAccountId=deprecated_link.bankAccountId,
            )
            db.session.add(deprecated_log)
        link = offerers_models.VenueBankAccountLink(
            bankAccount=bank_account, venue=venue, timespan=(datetime.utcnow(),)
        )
        created_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
            venue=venue,
            bankAccount=bank_account,
        )
        db.session.add(created_log)
        db.session.add(link)
        return link

    def keep_track_of_bank_account_status_changes(self, bank_account: finance_models.BankAccount) -> None:
        now = datetime.utcnow()
        if bank_account.statusHistory:
            current_link = bank_account.statusHistory[0]
            if current_link.status == bank_account.status:
                logger.info(
                    "bank_account status did not change. Nothing to track.",
                    extra={
                        "application_id": self.application_details.application_id,
                        "bank_account_id": bank_account.id,
                        "bank_account_status": bank_account.status,
                    },
                )
                return
            current_link.timespan = make_timerange(start=current_link.timespan.lower, end=now)
            db.session.add(current_link)

        bank_account_status_history = finance_models.BankAccountStatusHistory(
            bankAccount=bank_account, status=bank_account.status, timespan=(now,)
        )
        db.session.add(bank_account_status_history)

    def archive_dossier(self) -> None:
        if self.application_details.status not in (
            BankAccountApplicationStatus.DRAFT,
            BankAccountApplicationStatus.ON_GOING,
            BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS,
        ):
            logger.info("Archiving application", extra={"application_id": self.application_details.application_id})
            archive_dossier(self.application_details.dossier_id)

    def validated_bank_account_email_notification(
        self, bank_account: finance_models.BankAccount, new_linked_venue: offerers_models.Venue | None
    ) -> None:
        if self.application_details.status != BankAccountApplicationStatus.ACCEPTED:
            return

        offerer_id = bank_account.offerer.id
        venue_id = new_linked_venue.id if new_linked_venue else None

        has_non_free_offers_subquery = (
            sqla.select(1)
            .select_from(offers_models.Stock)
            .join(
                offers_models.Offer,
                sqla.and_(
                    offers_models.Stock.offerId == offers_models.Offer.id,
                    offers_models.Stock.price > 0,
                    offers_models.Stock.isSoftDeleted.is_(False),
                    offers_models.Offer.isActive.is_(True),
                    offers_models.Offer.venueId == offerers_models.Venue.id,
                ),
            )
            .correlate(offerers_models.Venue)
            .exists()
        )

        has_non_free_collective_offers_subquery = (
            sqla.select(1)
            .select_from(educational_models.CollectiveStock)
            .join(
                educational_models.CollectiveOffer,
                sqla.and_(
                    educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
                    educational_models.CollectiveStock.price > 0,
                    educational_models.CollectiveOffer.isActive.is_(True),
                    educational_models.CollectiveOffer.venueId == offerers_models.Venue.id,
                ),
            )
            .correlate(offerers_models.Venue)
            .exists()
        )

        venues = (
            offerers_models.Venue.query.filter(
                offerers_models.Venue.managingOffererId == offerer_id,
                offerers_models.Venue.id != venue_id,
                sqla.or_(has_non_free_offers_subquery, has_non_free_collective_offers_subquery),
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sqla.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                ),
                isouter=True,
            )
            .options(
                sqla_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
                .load_only(offerers_models.VenueBankAccountLink.id)
                .load_only(offerers_models.VenueBankAccountLink.timespan)
            )
            .all()
        )
        for venue in venues:
            if not venue.current_bank_account_link and venue.bookingEmail:
                transactional_mails.send_bank_account_validated_email(venue.bookingEmail)


class ImportBankAccountV4(AbstractImportBankAccount, ImportBankAccountMixin):
    def execute(self) -> None:
        venue = self.get_venue()

        if not venue:
            return

        bank_account = self.get_or_create_bank_account(venue.managingOfferer, venue)
        self.keep_track_of_bank_account_status_changes(bank_account)
        self.link_venue_to_bank_account(bank_account, venue)
        self.validated_bank_account_email_notification(bank_account, venue)
        self.archive_dossier()

    def get_venue(self) -> "Venue | None":
        """
        Fetch the venue given the DS token of the application.
        """
        venue = (
            offerers_models.Venue.query.filter(offerers_models.Venue.dmsToken == self.application_details.dms_token)
            .options(
                sqla_orm.load_only(
                    offerers_models.Venue.id, offerers_models.Venue.publicName, offerers_models.Venue.name
                )
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sqla.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                ),
            )
            .options(
                sqla_orm.contains_eager(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.id)
            )
            .options(sqla_orm.contains_eager(offerers_models.Venue.bankAccountLinks))
            .one_or_none()
        )
        if venue is None:
            logger.info(
                "Venue not found with DS token",
                extra={
                    "application_id": self.application_details.application_id,
                    "ds_token": self.application_details.dms_token,
                },
            )
        return venue


class ImportBankAccountV5(AbstractImportBankAccount, ImportBankAccountMixin):
    def execute(self) -> None:
        if not self.application_details.siren:
            logger.info(
                "siren can't be None in DSv5 context", extra={"application_id": self.application_details.application_id}
            )
            return

        venue = self.get_venue()

        if not venue:
            offerer = self.get_offerer()
            if not offerer:
                return
        else:
            offerer = venue.managingOfferer

        bank_account = self.get_or_create_bank_account(offerer, venue)
        self.keep_track_of_bank_account_status_changes(bank_account)
        if venue:
            self.link_venue_to_bank_account(bank_account, venue)
        self.validated_bank_account_email_notification(bank_account, venue)
        self.archive_dossier()

    def get_venue(self) -> "Venue | None":
        """
        Fetch a venue among physical ones of the offerer.
        Return None if no existing venues or more than one.
        """
        venues = (
            offerers_models.Venue.query.filter(
                offerers_models.Offerer.siren == self.application_details.siren,
                offerers_models.Venue.isVirtual == False,
            )
            .options(
                sqla_orm.load_only(
                    offerers_models.Venue.id, offerers_models.Venue.publicName, offerers_models.Venue.name
                )
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sqla.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                ),
            )
            .options(
                sqla_orm.contains_eager(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.id)
            )
            .options(sqla_orm.contains_eager(offerers_models.Venue.bankAccountLinks))
            .all()
        )
        if not venues or len(venues) > 1:
            logger.info(
                "Can't link a BankAccount to a venue",
                extra={
                    "siren": self.application_details.siret,
                    "application_id": self.application_details.application_id,
                    "has_venues": bool(venues),
                },
            )
            return None
        return venues[0]

    def get_offerer(self) -> "Offerer | None":
        assert self.application_details.siren  # helps mypy
        offerer = (
            offerers_models.Offerer.query.filter_by(siren=self.application_details.siren)
            .options(sqla_orm.load_only(offerers_models.Offerer.id))
            .one_or_none()
        )
        if not offerer:
            logger.info(
                "Can't find an offerer by siren",
                extra={
                    "application_id": self.application_details.application_id,
                    "siren": self.application_details.siren,
                },
            )
        return offerer


class ImportBankAccountFactory:
    procedure_to_class = {
        4: ImportBankAccountV4,
        5: ImportBankAccountV5,
    }

    @classmethod
    def get(cls, procedure_version: int) -> type["AbstractImportBankAccount"]:
        return cls.procedure_to_class[procedure_version]
