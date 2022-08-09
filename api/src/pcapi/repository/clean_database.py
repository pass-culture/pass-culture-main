from pcapi import settings
import pcapi.core.booking_providers.models as booking_providers_models
import pcapi.core.bookings.models as bookings_models
import pcapi.core.criteria.models as criteria_models
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
from pcapi.core.finance.models import BankInformation
import pcapi.core.fraud.models as fraud_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
from pcapi.local_providers.install import install_local_providers
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.feature import Feature
from pcapi.models.feature import install_feature_flags
from pcapi.models.user_session import UserSession


def clean_all_database(*args, **kwargs):  # type: ignore [no-untyped-def]
    """Order of deletions matters because of foreign key constraints"""
    if settings.ENV not in ("development", "testing"):
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")
    providers_models.LocalProviderEvent.query.delete()
    offers_models.ActivationCode.query.delete()
    providers_models.AllocineVenueProviderPriceRule.query.delete()
    providers_models.AllocineVenueProvider.query.delete()
    providers_models.VenueProvider.query.delete()
    finance_models.PaymentStatus.query.delete()
    finance_models.Payment.query.delete()
    finance_models.PaymentMessage.query.delete()
    finance_models.CashflowPricing.query.delete()
    finance_models.CashflowLog.query.delete()
    finance_models.InvoiceCashflow.query.delete()
    finance_models.Cashflow.query.delete()
    finance_models.CashflowBatch.query.delete()
    finance_models.PricingLine.query.delete()
    finance_models.PricingLog.query.delete()
    finance_models.Pricing.query.delete()
    finance_models.InvoiceLine.query.delete()
    finance_models.Invoice.query.delete()
    finance_models.BusinessUnitVenueLink.query.delete()
    payments_models.CustomReimbursementRule.query.delete()
    educational_models.CollectiveOfferDomain.query.delete()
    educational_models.CollectiveOfferTemplateDomain.query.delete()
    educational_models.EducationalDomain.query.delete()
    educational_models.CollectiveBooking.query.delete()
    bookings_models.ExternalBooking.query.delete()
    bookings_models.Booking.query.delete()
    bookings_models.IndividualBooking.query.delete()
    educational_models.CollectiveStock.query.delete()
    offers_models.Stock.query.delete()
    users_models.Favorite.query.delete()
    offers_models.Mediation.query.delete()
    criteria_models.OfferCriterion.query.delete()
    criteria_models.VenueCriterion.query.delete()
    criteria_models.Criterion.query.delete()
    educational_models.CollectiveOffer.query.delete()
    educational_models.CollectiveOfferTemplate.query.delete()
    offers_models.Offer.query.delete()
    offers_models.Product.query.delete()
    # Handle relationship loop: Venue->BusinessUnit->BankInformation->Venue.
    offerers_models.Venue.query.update({"businessUnitId": None}, synchronize_session=False)
    finance_models.BusinessUnit.query.delete()
    BankInformation.query.delete()
    providers_models.CDSCinemaDetails.query.delete()
    providers_models.CinemaProviderPivot.query.delete()
    providers_models.AllocinePivot.query.delete()
    providers_models.AllocineTheater.query.delete()
    booking_providers_models.VenueBookingProvider.query.delete()
    booking_providers_models.BookingProvider.query.delete()
    offerers_models.VenuePricingPointLink.query.delete()
    offerers_models.VenueReimbursementPointLink.query.delete()
    offerers_models.Venue.query.delete()
    offerers_models.VenueEducationalStatus.query.delete()
    offerers_models.UserOfferer.query.delete()
    offerers_models.ApiKey.query.delete()
    offerers_models.Offerer.query.delete()
    offerers_models.OffererTag.query.delete()
    payments_models.Recredit.query.delete()
    payments_models.Deposit.query.delete()
    BeneficiaryImportStatus.query.delete()
    BeneficiaryImport.query.delete()
    fraud_models.BeneficiaryFraudCheck.query.delete()
    fraud_models.BeneficiaryFraudReview.query.delete()
    users_models.Token.query.delete()
    offers_models.OfferValidationConfig.query.delete()
    users_models.UserSuspension.query.delete()
    users_models.User.query.delete()
    UserSession.query.delete()
    providers_models.Provider.query.delete()
    offerers_models.VenueType.query.delete()
    offerers_models.VenueLabel.query.delete()
    educational_models.EducationalBooking.query.delete()
    educational_models.EducationalDeposit.query.delete()
    educational_models.EducationalInstitution.query.delete()
    educational_models.EducationalYear.query.delete()
    educational_models.EducationalRedactor.query.delete()
    Feature.query.delete()
    db.session.execute(f"DELETE FROM {perm_models.role_permission_table.name};")
    perm_models.Permission.query.delete()
    perm_models.Role.query.delete()

    # Dans le cadre du projet EAC, notre partenaire Adage requête notre api sur le endpoint get_pre_bookings.
    # Ils récupèrent les pré-réservations EAC liées à un utilisateur EAC et stockent les ids en base.
    # Dans la phase de développement, ils se connectent sur notre environnement testing et récupèrent des données issues donc de nos sandbox.
    # Nous avons besoin que les ids soient fixes. Pour ce faire, il faut que la séquence d'ids sur les EducationalBookings recommence à 1 à chaque
    # nouvelle génération de la sandbox sur testing. C'est la raison de la commande ci-dessous.
    # A noter qu'en local la question ne se pose pas car l'instance de base de données est détruite puis reconstruite. L'id recommence donc nécessairement à 1
    db.session.execute("SELECT setval('educational_booking_id_seq', 1, FALSE)")

    db.session.commit()
    install_feature_flags()
    install_local_providers()
    perm_models.sync_db_permissions(db.session)
