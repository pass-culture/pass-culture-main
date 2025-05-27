import typing

import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

import pcapi.core.bookings.models as bookings_models
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.geography.models as geography_models
import pcapi.core.history.models as history_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.providers.models as providers_models
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


# Order of table to clean matters because of foreign key constraints
# They will be deleted in this order
tables_to_clean: list[type[Model]] = [
    achievements_models.Achievement,
    artist_models.Artist,
    artist_models.ArtistAlias,
    artist_models.ArtistProductLink,
    chronicles_models.ProductChronicle,
    chronicles_models.OfferChronicle,
    chronicles_models.Chronicle,
    providers_models.LocalProviderEvent,
    offers_models.ActivationCode,
    providers_models.AllocineVenueProvider,
    providers_models.VenueProvider,
    finance_models.PaymentStatus,
    finance_models.Payment,
    finance_models.PaymentMessage,
    finance_models.CashflowPricing,
    finance_models.CashflowLog,
    finance_models.InvoiceCashflow,
    finance_models.Cashflow,
    finance_models.CashflowBatch,
    finance_models.PricingLine,
    finance_models.PricingLog,
    finance_models.Pricing,
    finance_models.InvoiceLine,
    finance_models.Invoice,
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
    offers_models.EventWeekDayOpeningHours,
    offers_models.EventOpeningHours,
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
    fraud_models.ProductWhitelist,
    fraud_models.OrphanDmsApplication,
    fraud_models.BlacklistedDomainName,
    fraud_models.BeneficiaryFraudCheck,
    fraud_models.BeneficiaryFraudReview,
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
    if settings.ENV not in ("development", "testing"):
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
