from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import BeneficiaryBookingsSQLRepository
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.repository.favorite.favorite_sql_repository import FavoriteSQLRepository
from infrastructure.repository.pro_offerers.paginated_offerers_sql_repository import PaginatedOfferersSQLRepository
from infrastructure.repository.pro_offers.paginated_offers_recap_sql_repository import PaginatedOffersSQLRepository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from infrastructure.repository.stock_provider.stock_provider_fnac import StockProviderFnacRepository
from infrastructure.repository.stock_provider.stock_provider_libraires import StockProviderLibrairesRepository
from infrastructure.repository.stock_provider.stock_provider_praxiel import StockProviderPraxielRepository
from infrastructure.repository.stock_provider.stock_provider_titelive import StockProviderTiteLiveRepository
from infrastructure.repository.venue.venue_label.venue_label_sql_repository import VenueLabelSQLRepository
from infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import VenueWithBasicInformationSQLRepository
from infrastructure.repository.venue.venue_with_offerer_name.venue_with_offerer_name_sql_repository import VenueWithOffererNameSQLRepository
from infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from use_cases.add_contact_in_eligiblity_list import AddContactInEligibilityList
from use_cases.book_an_offer import BookAnOffer
from use_cases.cancel_a_booking import CancelABooking
from use_cases.get_bookings_for_beneficiary import GetBookingsForBeneficiary
from use_cases.get_venue_labels import GetVenueLabels
from use_cases.get_venues_by_pro_user import GetVenuesByProUser
from use_cases.list_favorites_of_beneficiary import ListFavoritesOfBeneficiary
from use_cases.list_offerers_for_pro_user import ListOfferersForProUser
from use_cases.list_offers_for_pro_user import ListOffersForProUser

beneficiary_bookings_repository = BeneficiaryBookingsSQLRepository()
booking_repository = BookingSQLRepository()
favorite_repository = FavoriteSQLRepository()
notification_service = MailjetNotificationService()
paginated_offer_repository = PaginatedOffersSQLRepository()
stock_repository = StockSQLRepository()
user_repository = BeneficiarySQLRepository()
venue_label_repository = VenueLabelSQLRepository()
venue_identifier_repository = VenueWithBasicInformationSQLRepository()
venue_with_offerer_informations_repository = VenueWithOffererNameSQLRepository()
paginated_offerers_repository = PaginatedOfferersSQLRepository()

api_libraires_stocks = StockProviderLibrairesRepository()
api_fnac_stocks = StockProviderFnacRepository()
api_titelive_stocks = StockProviderTiteLiveRepository()
api_praxiel_stocks = StockProviderPraxielRepository()

# Usecases
book_an_offer = BookAnOffer(booking_repository=booking_repository,
                            user_repository=user_repository,
                            stock_repository=stock_repository,
                            notification_service=notification_service)

cancel_a_booking = CancelABooking(
    booking_repository=booking_repository,
    notification_service=notification_service
)

get_venue_labels = GetVenueLabels(venue_label_repository=venue_label_repository)

get_all_venues_by_pro_user = GetVenuesByProUser(venue_repository=venue_with_offerer_informations_repository)

list_favorites_of_beneficiary = ListFavoritesOfBeneficiary(favorite_repository=favorite_repository)

list_offers_for_pro_user = ListOffersForProUser(paginated_offer_repository=paginated_offer_repository)

add_contact_in_eligibility_list = AddContactInEligibilityList(
    notification_service=notification_service
)

get_bookings_for_beneficiary = GetBookingsForBeneficiary(
    beneficiary_bookings_repository=beneficiary_bookings_repository)

list_offerers_for_pro_user = ListOfferersForProUser(paginated_offerers_repository=paginated_offerers_repository)
