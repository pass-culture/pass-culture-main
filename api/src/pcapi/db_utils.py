import typing

import sqlalchemy as sa
from sqlalchemy import exc as sa_exc
from sqlalchemy import text

import pcapi.core.bookings.models as bookings_models
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.geography.models as geography_models
import pcapi.core.highlights.models as highlights_models
import pcapi.core.history.models as history_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.providers.models as providers_models
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core.achievements import models as achievements_models
from pcapi.core.artist import models as artist_models
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.operations import models as operations_models
from pcapi.local_providers.install import install_local_providers
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.feature import Feature
from pcapi.models.feature import install_feature_flags


def install_database_extensions() -> None:
    _create_text_search_configuration_if_not_exists()
    _create_index_btree_gist_extension()
    _create_postgis_extension()


def _create_text_search_configuration_if_not_exists() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))

        french_unaccent_configuration_query = connection.execute(
            text("SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
        )
        if french_unaccent_configuration_query.fetchone() is None:
            connection.execute(text("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );"))
            connection.execute(
                text(
                    "ALTER TEXT SEARCH CONFIGURATION french_unaccent"
                    " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;"
                )
            )


def _create_index_btree_gist_extension() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))


def _create_postgis_extension() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))


# Order of table to clean matters because of foreign key constraints
# They will be deleted in this order
tables_to_clean: list[type[Model]] = [
    highlights_models.HighlightRequest,
    highlights_models.Highlight,
    achievements_models.Achievement,
    artist_models.Artist,
    artist_models.ArtistAlias,
    artist_models.ArtistProductLink,
    artist_models.ArtistOfferLink,
    chronicles_models.ProductChronicle,
    chronicles_models.OfferChronicle,
    chronicles_models.Chronicle,
    providers_models.LocalProviderEvent,
    offers_models.ActivationCode,
    providers_models.AllocineVenueProvider,
    providers_models.VenueProvider,
    offerers_models.NonPaymentNotice,
    finance_models.PaymentStatus,
    finance_models.Payment,
    finance_models.PaymentMessage,
    finance_models.CashflowPricing,
    finance_models.InvoiceCashflow,
    finance_models.Cashflow,
    finance_models.CashflowBatch,
    finance_models.PricingLine,
    finance_models.PricingLog,
    finance_models.Pricing,
    finance_models.InvoiceLine,
    finance_models.Invoice,
    finance_models.InvoiceSettlement,
    finance_models.Settlement,
    finance_models.SettlementBatch,
    finance_models.FinanceEvent,
    finance_models.CustomReimbursementRule,
    finance_models.BookingFinanceIncident,
    finance_models.FinanceIncident,
    finance_models.BankAccount,
    educational_models.CollectivePlaylist,
    educational_models.CollectiveOfferDomain,
    educational_models.CollectiveOfferTemplateDomain,
    educational_models.EducationalDomain,
    educational_models.CollectiveBooking,
    educational_models.CollectiveDmsApplication,
    educational_models.CollectiveOfferRequest,
    educational_models.CollectiveOfferTemplateEducationalRedactor,
    bookings_models.ExternalBooking,
    bookings_models.FraudulentBookingTag,
    bookings_models.Booking,
    educational_models.CollectiveStock,
    offers_models.Stock,
    users_models.Favorite,
    offers_models.Mediation,
    criteria_models.OfferCriterion,
    criteria_models.VenueCriterion,
    criteria_models.Criterion,
    criteria_models.CriterionCategory,
    educational_models.CollectiveOffer,
    educational_models.CollectiveOfferTemplate,
    offers_models.Offer,
    offers_models.PriceCategory,
    offers_models.PriceCategoryLabel,
    offers_models.Product,
    offers_models.OfferQuality,
    providers_models.CDSCinemaDetails,
    providers_models.BoostCinemaDetails,
    providers_models.CGRCinemaDetails,
    providers_models.EMSCinemaDetails,
    providers_models.CinemaProviderPivot,
    providers_models.AllocinePivot,
    providers_models.AllocineTheater,
    offerers_models.OffererConfidenceRule,
    offerers_models.VenuePricingPointLink,
    offerers_models.Venue,
    offerers_models.VenueEducationalStatus,
    offerers_models.UserOfferer,
    offerers_models.OffererProvider,
    offerers_models.ApiKey,
    offerers_models.Offerer,
    offerers_models.OffererStats,
    offerers_models.OffererTag,
    offerers_models.OffererTagCategory,
    offerers_models.OffererAddress,
    geography_models.Address,
    finance_models.Recredit,
    finance_models.Deposit,
    BeneficiaryImportStatus,
    BeneficiaryImport,
    fraud_models.BlacklistedDomainName,
    fraud_models.ProductWhitelist,
    subscription_models.BeneficiaryFraudCheck,
    subscription_models.BeneficiaryFraudReview,
    subscription_models.OrphanDmsApplication,
    offers_models.OfferValidationSubRule,
    offers_models.OfferValidationRule,
    offers_models.OfferPriceLimitationRule,
    operations_models.SpecialEventAnswer,
    operations_models.SpecialEventResponse,
    operations_models.SpecialEventQuestion,
    operations_models.SpecialEvent,
    users_models.GdprUserAnonymization,
    users_models.GdprUserDataExtract,
    users_models.SingleSignOn,
    users_models.UserProfileRefreshCampaign,
    users_models.UserTagCategoryMapping,
    users_models.UserTagCategory,
    users_models.UserTagMapping,
    users_models.UserTag,
    users_models.UserAccountUpdateRequest,
    users_models.User,
    users_models.UserSession,
    geography_models.IrisFrance,
    providers_models.Provider,
    offerers_models.VenueLabel,
    educational_models.EducationalDeposit,
    educational_models.EducationalInstitution,
    educational_models.EducationalYear,
    educational_models.EducationalRedactor,
    Feature,
    perm_models.RolePermission,
    perm_models.Permission,
    perm_models.Role,
    history_models.ActionHistory,
    educational_models.NationalProgram,
    dms_models.LatestDmsImport,
]


def clean_all_database(*args: typing.Any, reset_ids: bool = False, **kwargs: typing.Any) -> None:
    if settings.ENV not in ("development", "testing", "ops"):
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")

    for table in tables_to_clean:
        try:
            db.session.query(table).delete()
            if reset_ids:
                # Reset sequence id to 1 to have consistent ids in testing environment
                # This is mandatory for EAC bookings which are used by Adage (external partner)
                db.session.execute(
                    sa.text(
                        """DO $$
                        BEGIN
                            IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = '{table.__tablename__}_id_seq') THEN
                                EXECUTE 'SELECT setval(''{table.__tablename__}_id_seq'', 1, false)';
                            END IF;
                        END $$;
                        """.format(table=table)
                    )
                )
        except sa_exc.ProgrammingError:
            # If the table does not exist, it will raise a ProgrammingError
            # We don't want to fail the migration if the table does not exist, while trying to delete it
            pass

    db.session.commit()
    install_feature_flags()
    install_local_providers()
    perm_models.sync_db_permissions(db.session)
    perm_models.sync_db_roles(db.session)

def clean_e2e_data(user_id: int) -> None:
    """Delete all database data related to a given user for e2e test cleanup.

    Cascades through the FK graph starting from the user to find and delete
    all related entities in the correct dependency order.
    """
    if settings.ENV not in ("development", "testing", "ops"):
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")

    offerer_ids = _fetch_related_ids(
        'SELECT "offererId" FROM user_offerer WHERE "userId" = :user_id',
        {"user_id": user_id},
    )
    venue_ids = _fetch_related_ids(
        'SELECT id FROM venue WHERE "managingOffererId" = ANY(:ids)',
        {"ids": offerer_ids},
    ) if offerer_ids else []
    offer_ids = _fetch_related_ids(
        'SELECT id FROM offer WHERE "venueId" = ANY(:ids)',
        {"ids": venue_ids},
    ) if venue_ids else []
    stock_ids = _fetch_related_ids(
        'SELECT id FROM stock WHERE "offerId" = ANY(:ids)',
        {"ids": offer_ids},
    ) if offer_ids else []
    booking_ids = _fetch_related_ids(
        'SELECT id FROM booking WHERE "stockId" = ANY(:ids)',
        {"ids": stock_ids},
    ) if stock_ids else []
    collective_offer_ids = _fetch_related_ids(
        'SELECT id FROM collective_offer WHERE "venueId" = ANY(:ids)',
        {"ids": venue_ids},
    ) if venue_ids else []
    collective_stock_ids = _fetch_related_ids(
        'SELECT id FROM collective_stock WHERE "collectiveOfferId" = ANY(:ids)',
        {"ids": collective_offer_ids},
    ) if collective_offer_ids else []
    collective_offer_template_ids = _fetch_related_ids(
        'SELECT id FROM collective_offer_template WHERE "venueId" = ANY(:ids)',
        {"ids": venue_ids},
    ) if venue_ids else []
    bank_account_ids = _fetch_related_ids(
        'SELECT id FROM bank_account WHERE "offererId" = ANY(:ids)',
        {"ids": offerer_ids},
    ) if offerer_ids else []

    _delete_finance_data(booking_ids, bank_account_ids, venue_ids)
    _delete_booking_data(booking_ids, collective_stock_ids)
    _delete_stock_data(stock_ids, collective_stock_ids)
    _delete_offer_data(offer_ids, collective_offer_ids, collective_offer_template_ids)
    _delete_venue_data(venue_ids)
    _delete_action_history(user_id, offerer_ids, venue_ids)
    _delete_offerer_data(user_id, offerer_ids, bank_account_ids)
    _delete_user_data(user_id)

    db.session.commit()


def _fetch_related_ids(query: str, params: dict[str, typing.Any]) -> list[int]:
    """Execute a SELECT query and return the first column as a list of ints."""
    result = db.session.execute(sa.text(query), params)
    return [row[0] for row in result]


def _delete_by_ids(table_name: str, column: str, ids: list[int]) -> None:
    """Delete rows from a table where a column matches any of the given IDs."""
    if not ids:
        return
    db.session.execute(
        sa.text(f'DELETE FROM {table_name} WHERE {column} = ANY(:ids)'),
        {"ids": ids},
    )


def _delete_by_user_id(table_name: str, user_id: int) -> None:
    """Delete rows from a table where userId matches the given user ID."""
    db.session.execute(
        sa.text(f'DELETE FROM {table_name} WHERE "userId" = :user_id'),
        {"user_id": user_id},
    )


def _delete_finance_data(
    booking_ids: list[int],
    bank_account_ids: list[int],
    venue_ids: list[int],
) -> None:
    """Delete finance-related data (pricing, invoices, cashflows, incidents)."""
    pricing_ids = _fetch_related_ids(
        'SELECT id FROM pricing WHERE "bookingId" = ANY(:ids)',
        {"ids": booking_ids},
    ) if booking_ids else []
    _delete_by_ids("cashflow_pricing", '"pricingId"', pricing_ids)
    _delete_by_ids("pricing_line", '"pricingId"', pricing_ids)
    _delete_by_ids("pricing_log", '"pricingId"', pricing_ids)
    _delete_by_ids("pricing", "id", pricing_ids)

    invoice_ids = _fetch_related_ids(
        'SELECT id FROM invoice WHERE "bankAccountId" = ANY(:ids)',
        {"ids": bank_account_ids},
    ) if bank_account_ids else []
    cashflow_ids = _fetch_related_ids(
        'SELECT id FROM cashflow WHERE "bankAccountId" = ANY(:ids)',
        {"ids": bank_account_ids},
    ) if bank_account_ids else []
    _delete_by_ids("invoice_cashflow", '"invoiceId"', invoice_ids)
    _delete_by_ids("invoice_cashflow", '"cashflowId"', cashflow_ids)
    _delete_by_ids("invoice_line", '"invoiceId"', invoice_ids)
    _delete_by_ids("invoice", "id", invoice_ids)
    _delete_by_ids("cashflow_pricing", '"cashflowId"', cashflow_ids)
    _delete_by_ids("cashflow", "id", cashflow_ids)

    finance_incident_ids = _fetch_related_ids(
        'SELECT id FROM finance_incident WHERE "venueId" = ANY(:ids)',
        {"ids": venue_ids},
    ) if venue_ids else []
    _delete_by_ids("booking_finance_incident", '"incidentId"', finance_incident_ids)
    _delete_by_ids("finance_incident", "id", finance_incident_ids)


def _delete_booking_data(booking_ids: list[int], collective_stock_ids: list[int]) -> None:
    """Delete booking-related data."""
    _delete_by_ids("finance_event", '"bookingId"', booking_ids)
    _delete_by_ids("booking_finance_incident", '"bookingId"', booking_ids)
    _delete_by_ids("external_booking", '"bookingId"', booking_ids)
    _delete_by_ids("fraudulent_booking_tag", '"bookingId"', booking_ids)
    _delete_by_ids("booking", "id", booking_ids)
    _delete_by_ids("collective_booking", '"collectiveStockId"', collective_stock_ids)


def _delete_stock_data(stock_ids: list[int], collective_stock_ids: list[int]) -> None:
    """Delete stock-related data."""
    _delete_by_ids("activation_code", '"stockId"', stock_ids)
    _delete_by_ids("stock", "id", stock_ids)
    _delete_by_ids("collective_stock", "id", collective_stock_ids)


def _delete_offer_data(
    offer_ids: list[int],
    collective_offer_ids: list[int],
    collective_offer_template_ids: list[int],
) -> None:
    """Delete offer-related data."""
    _delete_by_ids("mediation", '"offerId"', offer_ids)
    _delete_by_ids("offer_criterion", '"offerId"', offer_ids)
    _delete_by_ids("price_category", '"offerId"', offer_ids)
    _delete_by_ids("collective_offer_domain", '"collectiveOfferId"', collective_offer_ids)
    _delete_by_ids("collective_offer_request", '"collectiveOfferId"', collective_offer_ids)
    _delete_by_ids(
        "collective_offer_template_domain",
        '"collectiveOfferTemplateId"',
        collective_offer_template_ids,
    )
    _delete_by_ids("offer", "id", offer_ids)
    _delete_by_ids("collective_offer", "id", collective_offer_ids)
    _delete_by_ids("collective_offer_template", "id", collective_offer_template_ids)


def _delete_venue_data(venue_ids: list[int]) -> None:
    """Delete venue-related data."""
    if venue_ids:
        venue_provider_ids = _fetch_related_ids(
            'SELECT id FROM venue_provider WHERE "venueId" = ANY(:ids)',
            {"ids": venue_ids},
        )
        _delete_by_ids("allocine_venue_provider", "id", venue_provider_ids)
    _delete_by_ids("venue_provider", '"venueId"', venue_ids)
    _delete_by_ids("venue_pricing_point_link", '"venueId"', venue_ids)
    _delete_by_ids("venue_criterion", '"venueId"', venue_ids)
    _delete_by_ids("price_category_label", '"venueId"', venue_ids)
    _delete_by_ids("venue", "id", venue_ids)


def _delete_action_history(
    user_id: int,
    offerer_ids: list[int],
    venue_ids: list[int],
) -> None:
    """Delete action history records related to the user, offerers, or venues."""
    db.session.execute(
        sa.text(
            'DELETE FROM action_history '
            'WHERE "userId" = :user_id '
            'OR "authorUserId" = :user_id '
            'OR "offererId" = ANY(:offerer_ids) '
            'OR "venueId" = ANY(:venue_ids)'
        ),
        {
            "user_id": user_id,
            "offerer_ids": offerer_ids or [],
            "venue_ids": venue_ids or [],
        },
    )


def _delete_offerer_data(
    user_id: int,
    offerer_ids: list[int],
    bank_account_ids: list[int],
) -> None:
    """Delete offerer-related data and the user-offerer link."""
    _delete_by_ids("bank_account", "id", bank_account_ids)
    _delete_by_ids("offerer_provider", '"offererId"', offerer_ids)
    _delete_by_ids("offerer_confidence_rule", '"offererId"', offerer_ids)
    _delete_by_ids("non_payment_notice", '"offererId"', offerer_ids)
    _delete_by_ids("custom_reimbursement_rule", '"offererId"', offerer_ids)
    db.session.execute(
        sa.text('DELETE FROM user_offerer WHERE "userId" = :user_id'),
        {"user_id": user_id},
    )
    _delete_by_ids("offerer", "id", offerer_ids)


def _delete_user_data(user_id: int) -> None:
    """Delete data directly owned by the user, then the user itself."""
    deposit_ids = _fetch_related_ids(
        'SELECT id FROM deposit WHERE "userId" = :user_id',
        {"user_id": user_id},
    )
    _delete_by_ids("recredit", '"depositId"', deposit_ids)
    _delete_by_user_id("deposit", user_id)
    _delete_by_user_id("favorite", user_id)

    beneficiary_import_ids = _fetch_related_ids(
        'SELECT id FROM beneficiary_import WHERE "beneficiaryId" = :user_id',
        {"user_id": user_id},
    )
    _delete_by_ids("beneficiary_import_status", '"beneficiaryImportId"', beneficiary_import_ids)
    _delete_by_ids("beneficiary_import", "id", beneficiary_import_ids)

    _delete_by_user_id("beneficiary_fraud_check", user_id)
    _delete_by_user_id("beneficiary_fraud_review", user_id)
    _delete_by_user_id("user_session", user_id)
    _delete_by_user_id("single_sign_on", user_id)
    _delete_by_user_id("user_email_history", user_id)
    _delete_by_user_id("trusted_device", user_id)
    _delete_by_user_id("login_device_history", user_id)
    _delete_by_user_id("gdpr_user_data_extract", user_id)
    _delete_by_user_id("gdpr_user_anonymization", user_id)
    _delete_by_user_id("user_account_update_request", user_id)

    db.session.execute(
        sa.text('DELETE FROM "user" WHERE id = :user_id'),
        {"user_id": user_id},
    )
