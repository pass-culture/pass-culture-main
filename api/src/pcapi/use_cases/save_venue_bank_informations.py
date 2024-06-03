from datetime import datetime
import logging
from textwrap import shorten
import typing

import schwifty
import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm

from pcapi import settings
from pcapi.connectors.dms.serializer import ApplicationDetail
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.domain.demarches_simplifiees import archive_dossier
from pcapi.domain.demarches_simplifiees import update_demarches_simplifiees_text_annotations
from pcapi.models import db


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Venue, Offerer

from pcapi.utils.db import make_timerange


logger = logging.getLogger(__name__)

PROCEDURE_ID_VERSION_MAP = {
    settings.DMS_VENUE_PROCEDURE_ID_V4: 4,
    settings.DS_BANK_ACCOUNT_PROCEDURE_ID: 5,
}


class AbstractImportBankAccount:
    def __init__(self, application_details: ApplicationDetail) -> None:
        self.application_details = application_details

    def execute(self) -> None:
        raise NotImplementedError()

    def get_venue(self) -> "Venue | None":
        raise NotImplementedError()


class ImportBankAccountMixin:
    # Let mypy know this class is going to be mixed with a child of `AbstractImportBankAccount`
    application_details: ApplicationDetail

    def is_iban_valid(self) -> bool:
        try:
            schwifty.IBAN(self.application_details.iban)
        except schwifty.exceptions.SchwiftyException:
            return False
        return True

    def is_bic_valid(self) -> bool:
        try:
            schwifty.BIC(self.application_details.bic)
        except schwifty.exceptions.SchwiftyException:
            return False
        return True

    def validate_bic_and_iban(self) -> bool:
        """
        We can't do this checks inside a pydantic validator
        because some business logic is tied to whether or not
        the IBAN/BIC are valid.
        If not, we need to annotate the application
        for the compliance.
        """
        if not self.is_bic_valid():
            self.annotate_application("Le BIC n'est pas valide")
            return False

        if not self.is_iban_valid():
            self.annotate_application("L'IBAN n'est pas valide")
            return False

        return True

    def get_or_create_bank_account(
        self,
        offerer: offerers_models.Offerer,
        venue: "Venue | None" = None,
    ) -> tuple[finance_models.BankAccount, bool]:
        """
        Retrieve a bankAccount if already existing and update the status
        or create it and fill it with DS metadata.
        """
        created = False
        bank_account = (
            finance_models.BankAccount.query.filter_by(dsApplicationId=self.application_details.application_id)
            .options(sqla_orm.load_only(finance_models.BankAccount.id))
            .outerjoin(
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
                label = shorten(label, width=100, placeholder="...")
            bank_account = finance_models.BankAccount(
                iban=self.application_details.iban,
                bic=self.application_details.bic,
                label=label,
                offerer=offerer,
                dsApplicationId=self.application_details.application_id,
            )
            created = True
        bank_account.status = self.application_details.status
        db.session.add(bank_account)
        db.session.flush()
        return bank_account, created

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

    def deprecate_venue_bank_account_links(self, bank_account: finance_models.BankAccount) -> None:
        """Most of the time, the below operation will be useless, because when a DS application
        hasn't been accepted by the compliance, the pro users don't have the possibility to link a venue to it.
        However, the DS interface allow to accept an application, set it back to `on_going` and finally
        reject it. During the time it was accepted, it is possible for a pro user to link a venue
        to this bank account. And we can have a situation where we generate cashflows for a bank account
        that have been rejected.
        Hence that operation.
        """
        finance_api.deprecate_venue_bank_account_links(bank_account)

    def annotate_application(self, message: str) -> None:
        """
        Annotate the application with the rightfull message at the end of the automated process.
        Prepend if private annotation already exists
        """
        if self.application_details.error_annotation_value:
            if message in self.application_details.error_annotation_value:
                return
            message = f"{message}, {self.application_details.error_annotation_value}"

        update_demarches_simplifiees_text_annotations(
            dossier_id=self.application_details.dossier_id,
            annotation_id=self.application_details.error_annotation_id,
            message=message,
        )


class ImportBankAccountV4(AbstractImportBankAccount, ImportBankAccountMixin):
    def execute(self) -> None:
        venue = self.get_venue()

        if not venue:
            return

        if not self.validate_bic_and_iban():
            return

        bank_account, created = self.get_or_create_bank_account(venue.managingOfferer, venue)
        if not created and not self.application_details.is_accepted:
            self.deprecate_venue_bank_account_links(bank_account)
        self.keep_track_of_bank_account_status_changes(bank_account)
        if self.application_details.is_accepted:
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

        if not self.validate_bic_and_iban():
            return

        bank_account, created = self.get_or_create_bank_account(offerer, venue)
        if not created and not self.application_details.is_accepted:
            self.deprecate_venue_bank_account_links(bank_account)
        self.keep_track_of_bank_account_status_changes(bank_account)
        if self.application_details.is_accepted and venue:
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
