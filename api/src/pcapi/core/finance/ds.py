import datetime
import logging
import typing
from textwrap import shorten

import schwifty
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.core.mails.transactional as transactional_mails
from pcapi import settings
from pcapi.connectors.dms import api as ds_api
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms.serializer import ApplicationDetail
from pcapi.connectors.dms.serializer import MarkWithoutContinuationApplicationDetail
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.db import make_timerange


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Offerer
    from pcapi.core.offerers.models import Venue


logger = logging.getLogger(__name__)

MARK_WITHOUT_CONTINUATION_MOTIVATION = "Classé sans suite et archivé automatiquement"  # visible in DS
PROCEDURE_ID_VERSION_MAP = {
    settings.DMS_VENUE_PROCEDURE_ID_V4: 4,
    settings.DS_BANK_ACCOUNT_PROCEDURE_ID: 5,
}
FIELD_NAME_TO_INTERNAL_NAME_MAPPING = {
    ("Prénom", "prénom"): "firstname",
    ("Nom", "nom"): "lastname",
    ("Mon numéro de téléphone",): "phone_number",
    ("IBAN",): "iban",
    ("BIC",): "bic",
    ("Intitulé du compte bancaire",): "label",
}
DMS_TOKEN_ID = "Q2hhbXAtMjY3NDMyMQ=="
ACCEPTED_DMS_STATUS = (dms_models.DmsApplicationStates.closed,)
DRAFT_DMS_STATUS = (
    dms_models.DmsApplicationStates.received,
    dms_models.DmsApplicationStates.initiated,
)
REJECTED_DMS_STATUS = (
    dms_models.DmsApplicationStates.refused,
    dms_models.DmsApplicationStates.without_continuation,
)
DMS_TOKEN_PRO_PREFIX = "PRO-"


def update_ds_applications_for_procedure(
    procedure_number: int,
    since: datetime.datetime | None,
    set_without_continuation: bool = False,
) -> list:
    logger.info("[DS] Started processing Bank Account procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient()
    application_numbers = []
    procedure_version = PROCEDURE_ID_VERSION_MAP[str(procedure_number)]

    for node in ds_client.get_pro_bank_nodes_states(procedure_number=procedure_number, since=since):
        data = parse_raw_bank_info_data(node, procedure_version)
        try:
            ImportBankAccount = ImportBankAccountFactory.get(procedure_version)
            application_details = ApplicationDetail(**{"application_type": procedure_version, **data})
            ImportBankAccount(application_details).execute()
        except Exception as exc:
            logger.exception(
                "[DS] Application parsing failed with error %s",
                str(exc),
                extra={
                    "application_number": node.get("number"),
                    "application_scalar_id": node.get("id"),
                    "procedure_number": procedure_number,
                },
            )
            # If we don't rollback here, we will persist in the faulty transaction
            # and we won't be able to commit at the end of the process and to set the current import `isProcessing` attr to False
            # Therefore, this import could be seen as on going for other next attempts, forever.
            db.session.rollback()
        else:
            application_numbers.append(node["number"])
            # Committing here ensures that we have a proper transaction for each application successfully imported
            # And that for each faulty application, the failure only impacts that particular one.
            db.session.commit()

    logger.info(
        "[DS] Finished processing Bank Account procedure %s.",
        procedure_number,
        extra={"procedure_number": procedure_number},
    )

    return application_numbers


def mark_without_continuation_applications() -> None:
    """
    Mark without continuation following applications:
        - All DSv4 that:
            - are in `draft` or `on_going` states
            - haven't been updated since DS_MARK_WITHOUT_CONTINUATION_APPLICATION_DEADLINE days
            - have the field `Erreur traitement Pass Culture` filled
                - without mention of `ADAGE` or without mention of `RCT`
                or
                - with mention of `RCT` and haven't been updated since DS_MARK_WITHOUT_CONTINUATION_ANNOTATION_DEADLINE days

        - All DSv5 that:
            - are in `draft` or `on_going` states
            - haven't been updated since DS_MARK_WITHOUT_CONTINUATION_APPLICATION_DEADLINE days
                and
                    - have the field `En attente de validation de structure` checked since more than DS_MARK_WITHOUT_CONTINUATION_ANNOTATION_DEADLINE days
                    - don't have the field `En attente de validation Adage` checked at all
                    or
                    - don't have the field `En attente de validation de structure` checked at all
                    - don't have the field `En attente de validation Adage` checked at all
    """
    procedures = [settings.DMS_VENUE_PROCEDURE_ID_V4, settings.DS_BANK_ACCOUNT_PROCEDURE_ID]
    states = [dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going]
    ds_client = ds_api.DMSGraphQLClient()

    for procedure in procedures:
        for state in states:
            for raw_node in ds_client.get_pro_bank_nodes_states(procedure_number=int(procedure), state=state):
                application = MarkWithoutContinuationApplicationDetail(**raw_node)

                try:
                    if application.should_be_marked_without_continuation:
                        logger.info(
                            "[DS] Found one application to mark `without_continuation`",
                            extra={"application_id": application.number},
                        )
                        ds_client.mark_without_continuation(
                            application_techid=application.id,
                            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                            motivation=MARK_WITHOUT_CONTINUATION_MOTIVATION,
                            from_draft=application.is_draft,
                        )
                        application.mark_without_continuation()
                        ds_client.archive_application(
                            application_techid=application.id,
                            instructeur_techid=settings.DS_MARK_WITHOUT_CONTINUATION_INSTRUCTOR_ID,
                        )
                        logger.info(
                            "[DS] Successfully mark `without_continuation` and archived an application",
                            extra={"application_id": application.number},
                        )
                except Exception:
                    logger.exception(
                        "Error while trying to mark without continuation an application",
                        extra={"application_id": application.number},
                    )
                    db.session.rollback()
                else:
                    db.session.commit()


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
            db.session.query(finance_models.BankAccount)
            .filter_by(dsApplicationId=self.application_details.application_id)
            .options(sa_orm.load_only(finance_models.BankAccount.id))
            .outerjoin(
                finance_models.BankAccountStatusHistory,
                sa.and_(
                    finance_models.BankAccountStatusHistory.bankAccountId == finance_models.BankAccount.id,
                    finance_models.BankAccountStatusHistory.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.VenueBankAccountLink.bankAccountId == finance_models.BankAccount.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .outerjoin(offerers_models.Venue, offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId)
            .options(sa_orm.contains_eager(finance_models.BankAccount.statusHistory))
            .options(
                sa_orm.contains_eager(finance_models.BankAccount.venueLinks)
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
            upper_bound = datetime.datetime.utcnow()
            timespan = make_timerange(start=lower_bound, end=upper_bound)
            deprecated_link.timespan = timespan
            deprecated_log = history_models.ActionHistory(
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                venueId=venue.id,
                bankAccountId=deprecated_link.bankAccountId,
            )
            db.session.add(deprecated_log)
        link = offerers_models.VenueBankAccountLink(
            bankAccount=bank_account, venue=venue, timespan=(datetime.datetime.utcnow(),)
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
        now = datetime.datetime.utcnow()
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
            sa.select(1)
            .select_from(offers_models.Stock)
            .join(
                offers_models.Offer,
                sa.and_(
                    offers_models.Stock.offerId == offers_models.Offer.id,
                    offers_models.Stock.price > 0,
                    offers_models.Stock.isSoftDeleted.is_(False),
                    offers_models.Offer.isActive,
                    offers_models.Offer.venueId == offerers_models.Venue.id,
                ),
            )
            .correlate(offerers_models.Venue)
            .exists()
        )

        has_non_free_collective_offers_subquery = (
            sa.select(1)
            .select_from(educational_models.CollectiveStock)
            .join(
                educational_models.CollectiveOffer,
                sa.and_(
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
            db.session.query(offerers_models.Venue)
            .filter(
                offerers_models.Venue.managingOffererId == offerer_id,
                offerers_models.Venue.id != venue_id,
                sa.or_(has_non_free_offers_subquery, has_non_free_collective_offers_subquery),
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
                ),
                isouter=True,
            )
            .options(
                sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
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

        ds_api.update_demarches_simplifiees_text_annotations(
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
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.dmsToken == self.application_details.dms_token)
            .options(
                sa_orm.load_only(offerers_models.Venue.id, offerers_models.Venue.publicName, offerers_models.Venue.name)
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .options(sa_orm.contains_eager(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.id))
            .options(sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks))
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
            db.session.query(offerers_models.Venue)
            .filter(
                offerers_models.Offerer.siren == self.application_details.siren,
                offerers_models.Venue.isVirtual == False,
            )
            .options(
                sa_orm.load_only(offerers_models.Venue.id, offerers_models.Venue.publicName, offerers_models.Venue.name)
            )
            .join(offerers_models.Offerer)
            .outerjoin(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .options(sa_orm.contains_eager(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.id))
            .options(sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks))
            .all()
        )
        if not venues or len(venues) > 1:
            logger.info(
                "Can't link a BankAccount to a venue",
                extra={
                    "siret": self.application_details.siret,
                    "application_id": self.application_details.application_id,
                    "has_venues": bool(venues),
                },
            )
            return None
        return venues[0]

    def get_offerer(self) -> "Offerer | None":
        assert self.application_details.siren  # helps mypy
        offerer = (
            db.session.query(offerers_models.Offerer)
            .filter_by(siren=self.application_details.siren)
            .options(sa_orm.load_only(offerers_models.Offerer.id))
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


def parse_raw_bank_info_data(data: dict, procedure_version: int) -> dict:
    result = {
        "status": data["state"],
        "updated_at": data["dateDerniereModification"],
        "last_pending_correction_date": data["dateDerniereCorrectionEnAttente"],
        "dossier_id": data["id"],
        "application_id": data["number"],
    }

    result["error_annotation_id"] = None
    result["venue_url_annotation_id"] = None
    for annotation in data["annotations"]:
        match annotation["label"]:
            case "Erreur traitement pass Culture" | "Annotation technique (réservée à pcapi)":
                result["error_annotation_id"] = annotation["id"]
                result["error_annotation_value"] = annotation["stringValue"]
            case "URL du lieu":
                result["venue_url_annotation_id"] = annotation["id"]
                result["venue_url_annotation_value"] = annotation["stringValue"]

    match procedure_version:
        case 4:
            _parse_v4_content(data, result)
        case 5:
            _parse_v5_content(data, result)

    return result


def _parse_v4_content(data: dict, result: dict) -> dict:
    for field in data["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
            elif field["id"] == DMS_TOKEN_ID:
                result["dms_token"] = _remove_dms_pro_prefix(field["value"].strip("  "))
    return result


def _parse_v5_content(data: dict, result: dict) -> dict:
    for field in data["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
    result["siret"] = data["demandeur"]["siret"]
    result["siren"] = result["siret"][:9]

    return result


def _remove_dms_pro_prefix(dms_token: str) -> str:
    if dms_token.startswith(DMS_TOKEN_PRO_PREFIX):
        return dms_token[len(DMS_TOKEN_PRO_PREFIX) :]
    return dms_token


def archive_dossier(dossier_id: str) -> None:
    client = ds_api.DMSGraphQLClient()
    client.archive_application(dossier_id, settings.DMS_INSTRUCTOR_ID)
