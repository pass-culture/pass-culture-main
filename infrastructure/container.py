from infrastructure.repository.beneficiary.beneficiary_jouve_repository import BeneficiaryJouveRepository
from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from infrastructure.repository.venue.venue_label.venue_label_sql_repository import VenueLabelSQLRepository
from infrastructure.repository.venue.venue_with_offerer_name.venue_with_offerer_name_sql_repository import VenueWithOffererNameSQLRepository
from infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import VenueWithBasicInformationSQLRepository
from infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from use_cases.book_an_offer import BookAnOffer
from use_cases.get_venues_by_pro_user import GetVenuesByProUser
from use_cases.get_venue_labels import GetVenueLabels
from use_cases.create_beneficiary_from_application import CreateBeneficiaryFromApplication

# Repositories
beneficiary_pre_subscription_repository = BeneficiaryJouveRepository
booking_repository = BookingSQLRepository()
user_repository = BeneficiarySQLRepository()
stock_repository = StockSQLRepository()
notification_service = MailjetNotificationService()
venue_label_repository = VenueLabelSQLRepository()
venue_identifier_repository = VenueWithBasicInformationSQLRepository()
venue_with_offerer_informations_repository = VenueWithOffererNameSQLRepository()

# Usecases
book_an_offer = BookAnOffer(booking_repository=booking_repository,
                            user_repository=user_repository,
                            stock_repository=stock_repository,
                            notification_service=notification_service)

create_beneficiary_from_application = CreateBeneficiaryFromApplication(
    beneficiary_pre_subscription_repository=beneficiary_pre_subscription_repository,
    beneficiary_repository=user_repository
)

get_venue_labels = GetVenueLabels(venue_label_repository=venue_label_repository)

get_all_venues_by_pro_user = GetVenuesByProUser(venue_repository=venue_with_offerer_informations_repository)
