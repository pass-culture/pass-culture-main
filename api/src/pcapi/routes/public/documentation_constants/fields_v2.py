# mypy: disable-error-code=call-overload

import copy

from pydantic import Field

from pcapi.core.offers.models import Offer
from pcapi.routes.public.documentation_constants import descriptions


_example_datetime_with_tz = "2025-07-24T14:00:00+02:00"


LIMIT_DESCRIPTION = "Number of items per page"

# Paths to docusaurus pages
CURSOR_PAGINATION_PAGE = "/docs/understanding-our-api/resources/cursor-pagination"
COLLECTIVE_OFFER_STATUS_PAGE = (
    "/docs/understanding-our-api/resources/collective-offers#collective-offer-status-and-allowed-actions"
)
# Anchors
GET_OFFERER_VENUES_ANCHOR = "#tag/Venues/operation/GetOffererVenues"
LIST_EDUCATIONAL_DOMAINS_ANCHOR = "#tag/Collective-Offer-Attributes/operation/ListEducationalDomains"
LIST_STUDENTS_LEVELS_ANCHOR = "#tag/Collective-Offer-Attributes/operation/ListStudentsLevels"
GET_NATIONAL_PROGRAMS_ANCHOR = "#tag/Collective-Offer-Attributes/operation/GetNationalPrograms"
LIST_EDUCATIONAL_INSTITUTIONS_ANCHOR = "#tag/Collective-Offer-Attributes/operation/ListEducationalInstitutions"


class _FIELDS_V2:
    """
    Naming convention:
        - `..._NOT_REQUIRED`: Field with `default=None`
        - `..._WITH_DEFAULT`: Field with default different from `None`, for instance `default=1`
    """

    def __getattribute__(self, name):  # type: ignore [no-untyped-def]
        """
        This is meant to avoid side-effects between classes that share a field.

        Without this, here what happens :

            from pydantic import BaseModel
            from pydantic import ConfigDict
            from pydantic import Field
            from pcapi.serialization.utils import to_camel

            MY_FIELD_CONSTANT = Field(description="a field description")

            class SomeResponseModel(BaseModel):
                name_of_the_field: str = MY_FIELD_CONSTANT

                # this will add an alias `nameOfTheField` to `MY_FIELD_CONSANT`
                model_config = ConfigDict(alias_generator=to_camel)

            class SomeOtherResponseModel(BaseModel):
                # now this model expects a field `nameOfTheField` instead of `another_field_name`
                # because of the `SomeResponseModel` class definition
                another_field_name: str = MY_FIELD_CONSTANT
        """
        return copy.deepcopy(super().__getattribute__(name))

    VENUE_ID = Field(
        example=535,
        description=f"Venue Id. The venues list is available on [**this endpoint (`Get offerer venues`)**]({GET_OFFERER_VENUES_ANCHOR})",
    )
    VENUE_ID_NOT_REQUIRED = Field(
        example=535,
        default=None,
        description=f"Venue Id. The venues list is available on [**this endpoint (`Get offerer venues`)**]({GET_OFFERER_VENUES_ANCHOR})",
    )
    DURATION_MINUTES = Field(
        description="Event duration in minutes",
        example=60,
    )
    ID_AT_PROVIDER = Field(
        description="Id of the object (product, event...) on your side. It should not be more than 70 characters long.",
        example="Your own id",
    )
    ID_AT_PROVIDER_WITH_MAX_LENGTH = Field(
        description="Id of the object (product, event...) on your side. It should not be more than 70 characters long.",
        example="Your own id",
        max_length=70,
    )
    PERIOD_BEGINNING_DATE = Field(
        description="Period beginning date. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
        example="2024-03-03T13:00:00+02:00",
    )
    PERIOD_ENDING_DATE = Field(
        description="Period ending date. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
        example="2024-05-10T15:00:00+02:00",
    )
    IDS_AT_PROVIDER_FILTER = Field(
        description="List of your ids to filter on (max 100)",
        example="5edd982915c2a74b9302e443,5edd982915e2a74vb9302e443",
    )

    # Pagination Fields
    PAGINATION_LIMIT_WITH_DEFAULT = Field(default=50, le=50, gt=0, description="Maximum number of items per page.")
    PAGINATION_FIRST_INDEX_WITH_DEFAULT = Field(
        default=1,
        ge=1,
        description=f"The page of results will be fetched starting from `firstIndex` (which is a resource id).**To learn more about cursor-based pagination [see this page]({CURSOR_PAGINATION_PAGE})**.",
    )

    # Image Fields
    IMAGE_CREDIT = Field(description="Image owner or author", example="Jane Doe")
    IMAGE_FILE = Field(
        description="Image file encoded in base64 string. Image format must be PNG or JPEG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format).",
    )
    IMAGE_URL = Field(description="Image URL publicly accessible", example="https://example.com/image.png")

    # Disability fields
    AUDIO_DISABILITY_COMPLIANT = Field(description="Is accessible for people with hearing disability", example=True)
    MENTAL_DISABILITY_COMPLIANT = Field(
        description="Is accessible for people with mental or cognitive disability", example=True
    )
    MOTOR_DISABILITY_COMPLIANT = Field(description="Is accessible for people with motor disability", example=True)
    VISUAL_DISABILITY_COMPLIANT = Field(description="Is accessible for people with visual disability", example=True)
    AUDIO_DISABILITY_COMPLIANT_WITH_DEFAULT = Field(
        False, description="Is accessible for people with hearing disability", example=True
    )
    MENTAL_DISABILITY_COMPLIANT_WITH_DEFAULT = Field(
        False, description="Is accessible for people with mental disability", example=True
    )
    MOTOR_DISABILITY_COMPLIANT_WITH_DEFAULT = Field(
        False, description="Is accessible for people with motor disability", example=True
    )
    VISUAL_DISABILITY_COMPLIANT_WITH_DEFAULT = Field(
        False, description="Is accessible for people with visual disability", example=True
    )

    # Address fields
    BAN_ID = Field(
        description="Id from the French **[Base nationale d'adresses](https://adresse.data.gouv.fr/)**",
        example="75101_8635_00182",  # Ban id of the French Ministry of Culture
    )
    BAN_ID_NOT_REQUIRED = Field(
        description="Id from the French **[Base nationale d'adresses](https://adresse.data.gouv.fr/)**",
        example="75101_8635_00182",  # Ban id of the French Ministry of Culture
        default=None,
    )
    LATITUDE = Field(description="Latitude coordinate", example=48.86696)
    LATITUDE_NOT_REQUIRED = Field(description="Latitude coordinate", example=48.86696, default=None)
    LONGITUDE = Field(description="Longitude coordinate", example=2.31014)
    LONGITUDE_NOT_REQUIRED = Field(description="Longitude coordinate", example=2.31014, default=None)
    CITY = Field(description="City", example="Paris")
    POSTAL_CODE = Field(description="Postal Code", example="75001")
    STREET = Field(description="Street name and number", example="182 Rue Saint-Honoré")
    ADDRESS_ID = Field(description="Address id in the pass Culture DB", example=1)
    ADDRESS_LABEL = Field(description="Address label", example="Zénith Paris")

    # Booking fields
    BOOKING_ID = Field(description="Booking id", example=12346)
    BOOKING_QUANTITY = Field(description="Booking quantity (can be either 1 or 2)", example=1)
    BOOKING_CREATION_DATE = Field(
        description="Booking creation date (ie. when the beneficiary booked the offer)",
        example=_example_datetime_with_tz,
    )
    BOOKING_CONFIRMATION_DATE_NOT_REQUIRED = Field(
        description="For event offers, deadline for cancellation by the beneficiary.",
        example=_example_datetime_with_tz,
        default=None,
    )

    # Offer fields
    OFFER_ID = Field(description="Offer id", example=12345)
    OFFER_ID_NOT_REQUIRED = Field(description="Offer id", example=12345, default=None)
    OFFER_STATUS = Field(description=descriptions.OFFER_STATUS_FIELD_DESCRIPTION, example="ACTIVE")
    OFFER_NAME = Field(description="Offer title", example="Le Petit Prince")
    OFFER_DESCRIPTION = Field(
        description="Offer description", example="A great book for kids and old kids.", max_length=1000
    )
    OFFER_NAME_WITH_MAX_LENGTH = Field(description="Offer title", example="Le Petit Prince", max_length=90)
    OFFER_DESCRIPTION = Field(
        description="Offer description",
        example="A great book for kids and old kids.",
    )
    OFFER_DESCRIPTION_WITH_MAX_LENGTH = Field(
        description="Offer description",
        example="A great book for kids and old kids.",
        max_length=10000,
    )
    OFFER_BOOKING_EMAIL = Field(
        description="Recipient email for notifications about bookings, cancellations, etc.",
        example="contact@yourcompany.com",
    )
    OFFER_BOOKING_CONTACT = Field(
        description="Recipient email to contact if there is an issue with booking the offer. Mandatory if the offer has withdrawable tickets.",
        example="support@yourcompany.com",
    )
    OFFER_PUBLICATION_DATETIME_WITH_DEFAULT = Field(
        description=descriptions.PUBLICATION_DATETIME_FIELD_DESCRIPTION,
        example=_example_datetime_with_tz,
        default="now",
    )
    OFFER_PUBLICATION_DATETIME = Field(
        description=descriptions.PUBLICATION_DATETIME_FIELD_DESCRIPTION,
        example=_example_datetime_with_tz,
    )
    OFFER_BOOKING_ALLOWED_DATETIME = Field(
        description=descriptions.BOOKING_ALLOWED_DATETIME_FIELD_DESCRIPTION,
        example=_example_datetime_with_tz,
        default=None,
    )
    DEPRECATED_OFFER_PUBLICATION_DATE = Field(
        description=descriptions.PUBLICATION_DATETIME_FIELD_DESCRIPTION,
        example=_example_datetime_with_tz,
    )
    OFFER_ENABLE_DOUBLE_BOOKINGS_WITH_DEFAULT = Field(
        description="If set to true, users may book the offer for two persons. Second item will be delivered at the same price as the first one. Category must be compatible with this feature.",
        example=True,
        default=False,
    )
    OFFER_ENABLE_DOUBLE_BOOKINGS_ENABLED = Field(
        description="If set to true, users may book the offer for two persons. Second item will be delivered at the same price as the first one. Category must be compatible with this feature.",
        example=True,
        default=True,
    )
    OFFER_LOCATION = Field(discriminator="type", description=descriptions.OFFER_LOCATION_DESCRIPTION)
    OFFER_ADDRESS_NOT_REQUIRED = Field(description="Offer address", example="4 rue des dames", default=None)
    OFFER_DEPARTEMENT_CODE_NOT_REQUIRED = Field(description="Offer departement code", example="63", default=None)

    # Products fields
    EANS_FILTER = Field(description="EANs list (max 100)", example="3700551782888,9782895761792")
    EAN = Field(
        description="European Article Number (EAN-13)",
        example="3700551782888",
    )
    EAN_NOT_REQUIRED = Field(
        description="European Article Number (EAN-13)",
        example="3700551782888",
        default=None,
    )
    EANS_AVAILABLE = Field(
        description="List of EANs that are available for upsert",
        example=["3700551782888", "9782895761792"],
    )
    EANS_REJECTED = Field(
        description="List of EANs that are not available for upsert, sorted by their rejection reasons",
    )
    EANS_REJECTED_BECAUSE_NOT_FOUND = Field(
        description="List of EANS not present in our database",
        example=["3700551782888", "9782895761792"],
    )
    EANS_REJECTED_BECAUSE_NOT_COMPLIANT = Field(
        description="List of EANS that do not comply with our CGU (General Terms and Conditions)",
        example=["3700551782888", "9782895761792"],
    )
    EANS_REJECTED_BECAUSE_CATEGORY_NOT_ALLOWED = Field(
        description="List of EANS that do not belong to an allowed category (only paper books, CDs, and vinyl records are permitted)",
        example=["3700551782888", "9782895761792"],
    )

    # Event fields
    PRICE_CATEGORY_ID = Field(description="Price category id", example=12)
    PRICE_CATEGORY_ID_NOT_REQUIRED = Field(description="Price category id", example=12, default=None)
    PRICE_CATEGORY_LABEL = Field(description="Price category label", example="Carré or")
    PRICE_CATEGORY_LABEL_NOT_REQUIRED = Field(description="Price category label", example="Carré or", default=None)
    PRICE_CATEGORIES = Field(description="Available price categories for this offer stocks")
    PRICE_CATEGORIES_WITH_MAX_ITEMS = Field(
        description="Available price categories for this offer stocks",
        max_items=Offer.MAX_PRICE_CATEGORIES_PER_OFFER,
    )
    BEGINNING_DATETIME = Field(
        description="Beginning datetime of the event. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
        example=_example_datetime_with_tz,
    )
    BEGINNING_DATETIME_NOT_REQUIRED = Field(
        description="Beginning datetime of the event. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
        example=_example_datetime_with_tz,
        default=None,
    )
    BOOKING_LIMIT_DATETIME = Field(
        description=descriptions.BOOKING_LIMIT_DATETIME_FIELD_DESCRIPTION,
        example=_example_datetime_with_tz,
    )
    EVENT_HAS_TICKET = Field(
        description="Indicated whether a ticket is mandatory to access to the event. True if it is the case, False otherwise. The ticket will be sent by you, the provider and you must have developed the pass Culture ticketing interface to do so.",
        example=False,
    )
    EVENT_DURATION = Field(description="Event duration in minutes", example=60)
    EVENT_STOCKS = Field(
        description="A list of stocks to associate with an event. Each stock represents a unique combination of a date and a price category. To add stocks for multiple price categories on the same date, you must create a separate stock entry for each category.",
        max_items=Offer.MAX_STOCKS_PER_OFFER,
    )
    EVENT_CATEGORIES_RELATED_FIELDS = Field(
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    EVENT_CATEGORY_ID = Field(description="Category id", example="CONCERT")
    EVENT_CATEGORY_LABEL = Field(description="Category label", example="Concert")
    EVENT_CONDITIONAL_FIELDS = Field(
        description="The keys are fields that should be set in the category_related_fields of an event. The values indicate whether their associated field is mandatory during event creation."
    )
    VIDEO_URL = Field(
        description="Video URL, must be from the Youtube plateform, it should be public and should not be a short nor a user's profile. To remove video from an offer, set to `null` ",
        example="https://www.youtube.com/watch?v=0R5PZxOgoz8",
    )

    # Booking fields
    BOOKING_STATUS = Field(description=descriptions.BOOKING_STATUS_DESCRIPTION, example="CONFIRMED")
    BOOKING_STATUS_NOT_REQUIRED = Field(
        description=descriptions.BOOKING_STATUS_DESCRIPTION, example="CONFIRMED", default=None
    )

    # Stock fields
    STOCK_EDITION = Field(
        description="If stock is set to null, all cancellable bookings (i.e not used) will be cancelled. To prevent from further bookings, you may alternatively set stock.quantity to the bookedQuantity (but not below).",
    )

    STOCK_ID = Field(description="Stock id", example=45)
    STOCK_ID_NOT_REQUIRED = Field(description="Stock id", example=45, default=None)
    QUANTITY = Field(
        description="Quantity of items currently available to pass Culture. Value `'unlimited'` is used for infinite quantity of items.",
        example=10,
    )
    PRICE = Field(description="Offer price in euro cents", example=1000)

    # Collective offer fields
    COLLECTIVE_OFFER_ID = Field(description="Collective offer id", example=12345)
    COLLECTIVE_OFFER_IDS = Field(description="List of collective offer ids", example=[12345, 67890])
    COLLECTIVE_OFFER_OFFER_STATUS = Field(
        description=f"Collective offer status - [see this page]({COLLECTIVE_OFFER_STATUS_PAGE})", example="PUBLISHED"
    )
    COLLECTIVE_OFFER_NAME = Field(description="Collective offer name", example="Atelier de peinture")
    COLLECTIVE_OFFER_DESCRIPTION = Field(
        description="Collective offer description", example="Atelier de peinture à la gouache pour élèves de 5ème"
    )
    COLLECTIVE_OFFER_FORMATS = Field(description="Educational Formats", example=["Atelier de pratique"])
    COLLECTIVE_OFFER_BOOKING_EMAILS = Field(
        description="Recipient emails for notifications about bookings, cancellations, etc.",
        example=["some@email.com", "some.other@email.com"],
    )
    COLLECTIVE_OFFER_CONTACT_EMAIL = Field(
        example="contact@yourcompany.com",
        description="Email of the person to contact if there is an issue with the offer.",
    )
    COLLECTIVE_OFFER_CONTACT_PHONE = Field(
        example="0123456789",
        description="Phone of the person to contact if there is an issue with the offer.",
    )
    COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS = Field(
        example=[1, 2],
        description=f"Educational domains ids linked to the offer. Those domains are available on **[this endpoint (`Get the eductional domains`)]({LIST_EDUCATIONAL_DOMAINS_ANCHOR})**",
    )
    COLLECTIVE_OFFER_STUDENT_LEVELS = Field(
        description=f"Student levels that can take pat to the collective offer. The student levels are available on [**this endpoint (`Get student levels eligible for collective offers`)**]({LIST_STUDENTS_LEVELS_ANCHOR})",
        example=["GENERAL2", "GENERAL1", "GENERAL0"],
    )
    COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID = Field(
        description=f"Id of the national program linked to your offer. The national programs list can be found on **[this endpoint (`Get all known national programs`)]({GET_NATIONAL_PROGRAMS_ANCHOR})**",
    )
    COLLECTIVE_OFFER_DATE_CREATED = Field(description="Collective offer creation date")
    COLLECTIVE_OFFER_START_DATETIME = Field(
        description="Collective offer start datetime. It cannot be a date in the past. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime). When creating a collective offer, the value of `startDatetime` will be copied to `endDatetime` if `endDatetime` is not provided.",
        example=_example_datetime_with_tz,
    )
    COLLECTIVE_OFFER_END_DATETIME = Field(
        description="Collective offer end datetime. It cannot be a date in the past. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime). When creating a collective offer, the value of `startDatetime` will be copied to `endDatetime` if `endDatetime` is not provided.",
        example=_example_datetime_with_tz,
    )
    COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME = Field(
        description="Booking limit datetime. It must be anterior to the `start_datetime`. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
        example=_example_datetime_with_tz,
    )
    COLLECTIVE_OFFER_TOTAL_PRICE = Field(
        example=100.00, description="Collective offer price (in €)", alias="totalPrice"
    )
    COLLECTIVE_OFFER_NB_OF_TICKETS = Field(example=10, description="Number of tickets for your collective offer")
    COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL = Field(
        description="The explanation of the offer price",
        example="10 tickets x 10 € = 100 €",
        alias="educationalPriceDetail",
    )
    # Collective booking
    COLLECTIVE_BOOKING_ID = Field(description="Collective booking id")
    COLLECTIVE_BOOKING_STATUS = Field(description="Collective booking status", example="PENDING")
    COLLECTIVE_BOOKING_DATE_CREATED = Field(description="When the booking was made")
    COLLECTIVE_BOOKING_CONFIRMATION_DATE = Field(description="When the booking was confirmed")
    COLLECTIVE_BOOKING_REIMBURSED_DATA = Field(description="When the booking was reimbursed")
    COLLECTIVE_BOOKING_DATE_USED = Field(description="When the booking was used")
    COLLECTIVE_BOOKING_CANCELLATION_LIMIT_DATE = Field(description="Deadline to cancel the booking")
    # Educational institution fields
    EDUCATIONAL_INSTITUTION_ID = Field(
        description=f"Educational institution id in the pass Culture application, should be `null` if an educational institution UAI is set. Institutions can be found on **[this endpoint (`Get all educational institutions`)]({LIST_EDUCATIONAL_INSTITUTIONS_ANCHOR})**",
        example=None,
    )
    EDUCATIONAL_INSTITUTION_UAI = Field(
        description=f'Educational institution UAI ("Unité Administrative Immatriculée") code. Institutions can be found on **[this endpoint (`Get all educational institutions`)]({LIST_EDUCATIONAL_INSTITUTIONS_ANCHOR})**',
        example="0010008D",
    )
    EDUCATIONAL_INSTITUTION_NAME = Field(
        description="Educational institution name",
        example="Lycée Pontus de Tyard",
    )
    EDUCATIONAL_INSTITUTION_TYPE = Field(
        description="Educational institution type",
        example="LYCEE GENERAL",
    )
    EDUCATIONAL_INSTITUTION_CITY = Field(
        description="City where the educational institution is located",
        example="Chalon-sur-Saône",
    )
    EDUCATIONAL_INSTITUTION_POSTAL_CODE = Field(
        description="Educational institution postal code",
        example="71100",
    )
    # Educational domain fields
    EDUCATIONAL_DOMAIN_ID = Field(description="Educational domain id", example=123456)
    EDUCATIONAL_DOMAIN_NAME = Field(description="Educational domain name", example="Cinéma, audiovisuel")
    # National program fields
    NATIONAL_PROGRAM_ID = Field(description="National program id", example=1223456)
    NATIONAL_PROGRAM_NAME = Field(description="National program name", example="Collège au cinéma")
    # Student level fields
    STUDENT_LEVEL_ID = Field(description="Student level id", example="COLLEGE6")
    STUDENT_LEVEL_NAME = Field(description="Student level name", example="Collège - 6e")

    # Provider fields
    PROVIDER_ID = Field(description="Provider id", example=123456)
    PROVIDER_NAME = Field(description="Provider name", example="Ultimate ticketing solution")
    PROVIDER_LOGO_URL_NOT_REQUIRED = Field(
        description="Provider logo url",
        example="https://ultimate-ticketing-solution.com/logo.png",
        default=None,
    )
    PROVIDER_NOTIFICATION_URL_NOT_REQUIRED = Field(
        description="Url on which booking notifications on offers you created are sent",
        example="https://ultimate-ticketing-solution.com/pass-culture-endpoint",
        default=None,
    )
    PROVIDER_BOOKING_URL_NOT_REQUIRED = Field(
        description="Url on which tickets requests for events you created are sent",
        example="https://ultimate-ticketing-solution.com/pass-culture-booking-endpoint",
        default=None,
    )
    PROVIDER_CANCEL_URL_NOT_REQUIRED = Field(
        description="Url on which tickets cancellation requests for events you created are sent",
        example="https://ultimate-ticketing-solution.com/pass-culture-cancellation-endpoint",
        default=None,
    )

    # User Fields
    USER_EMAIL = Field(description="Beneficiary email", example="michel.martin@somemail.fr")
    USER_PHONE_NUMBER_NOT_REQUIRED = Field(description="Beneficiary phone number", example="0612345678", default=None)
    USER_FIRST_NAME_NOT_REQUIRED = Field(description="Beneficiary first name", example="Michel", default=None)
    USER_LAST_NAME_NOT_REQUIRED = Field(description="Beneficiary last name", example="Martin", default=None)
    USER_BIRTH_DATE_NOT_REQUIRED = Field(
        description="Beneficiary birth date",
        example=_example_datetime_with_tz,
        default=None,
    )
    USER_BIRTH_DATE_NOT_REQUIRED = Field(
        description="Beneficiary birth date",
        example=_example_datetime_with_tz,
        default=None,
    )
    USER_POSTAL_CODE_NOT_REQUIRED = Field(description="Beneficiary postal code", example="75017", default=None)

    # Venue fields
    VENUE_ACTIVITY_DOMAIN = Field(description="Venue activity domain", example="RECORD_STORE")
    VENUE_SIRET_COMMENT = Field(description="Applicable if siret is null and venue is physical")
    VENUE_SIRET = Field(
        description="Venue siret. `null` when the venue is digital or when the `siretComment` field is not `null`.",
        example="85331845900049",
    )
    VENUE_CREATED_DATETIME = Field(description="When the venue was created")
    VENUE_LOCATION = Field(
        description="Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).",
        discriminator="type",
    )
    VENUE_LEGAL_NAME = Field(description="Venue legal name", example="SAS pass Culture")
    VENUE_PUBLIC_NAME = Field(
        description="Venue public name. If `null`, `legalName` is used instead.", example="pass Culture"
    )
    VENUE_NOTIFICATION_URL = Field(
        description="Url on which notifications for this venues will be sent. If not set, our system will use the notification url defined at provider level.",
        example="https://mysolution.com/pass-culture-endpoint",
    )
    VENUE_BOOKING_URL = Field(
        description="Url on which requests for tickets are sent when a beneficiary tries to book tickets for an event linked to this venue. If not set, our system will use the booking url defined at provider level.",
        example="https://my-ticketing-solution.com/pass-culture-booking-endpoint",
    )
    VENUE_CANCEL_URL = Field(
        description="Url on which tickets cancellation requests are sent when a beneficiary cancels its tickets for an event linked to this venue. If not set, our system will use the cancel url defined at provider level.",
        example="https://my-ticketing-solution.com/pass-culture-cancellation-endpoint",
    )
    ALLOWED_ON_ADAGE = Field(
        description="Can the offerer create collective offers?",
        example=True,
    )
    COLLECTIVE_OFFER_INTERVENTION_AREA = Field(description="Department codes (eg. '77', '2A')", example="75")

    COLLECTIVE_OFFER_LOCATION = Field(description=descriptions.COLLECTIVE_OFFER_LOCATION_DESCRIPTION, title="ADDRESS")
    COLLECTIVE_OFFER_LOCATION_TYPE = Field(
        description="Location type",
        example="SCHOOL",
    )
    COLLECTIVE_OFFER_LOCATION_ADDRESS_LABEL = Field(
        description="Address label",
        example="Zénith Paris",
    )
    COLLECTIVE_OFFER_LOCATION_ADDRESS_ID = Field(
        description="Address id in the pass Culture DB",
        example=1,
    )
    COLLECTIVE_OFFER_LOCATION_COMMENT = Field(
        description="Comment on the location",
        example="Lieu à définir avec l'organisateur",
    )
    COLLECTIVE_OFFER_LOCATION_IS_VENUE_ADDRESS = Field(
        description="Whether the offer is located at the address of the venue",
        example=True,
    )


fields_v2 = _FIELDS_V2()
