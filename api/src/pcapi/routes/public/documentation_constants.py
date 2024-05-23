from spectree import Tag


# HIGH LEVEL INFORMATION
PUBLIC_API_DESCRIPTION = """
This the documentation of the Pass Culture public REST API.

**Important notice:**
- Since January 2023, rate limiting has been implemented on the Pass Culture API.
  You are limited to **200 requests/minute** per API key.
  Once this limit reached, you will received a `429 Too Many Requests` error message. You will then need to back down.
- Dates of event offers are stored in the **UTC format** to be able to format them correctly, according to the user timezone, in our application interface.
- Any non-blank field sent using a `PATCH` method will be considered as changed, even if the new value is equal to old value.
  _For example, if you update the stock of an event, you **should not resend the `beginningDate`** if it has not changed because, otherwise it is going to trigger the reschedule process on our side._
"""

# FIELDS DESCRIPTIONS
OFFER_STATUS_FIELD_DESCRIPTION = """
Offer status:

- `ACTIVE`: offer is validated and active. \n\n
- `DRAFT`: offer is still draft and not yet submitted for validation - this status is not applicable to offers created via this API.\n\n
- `EXPIRED`: offer is validated but the booking limit datetime has passed.\n\n
- `INACTIVE`: offer is not active and cannot be booked.\n\n
- `PENDING`: offer is pending for pass Culture rules compliance validation. This step may last 72 hours.\n\n
- `REJECTED`: offer validation has been rejected because it is not compliant with pass Culture rules.\n\n
- `SOLD_OUT`: offer is validated but there is no (more) stock available for booking.
"""

BEGINNING_DATETIME_FIELD_DESCRIPTION = "Beginning datetime of the event. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime)."
BOOKING_LIMIT_DATETIME_FIELD_DESCRIPTION = "Datetime after which the offer can no longer be booked. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime)."

# BOOKING_TAGS
BOOKING_TAG = Tag(name="Booking", description="Endpoints to manage the bookings of an offer (event and product).")

# EVENT TAGS
EVENT_OFFER_INFO_TAG = Tag(
    name="Event offer", description="Endpoints to manage event offers data of a venue (except prices and dates)."
)
EVENT_OFFER_PRICES_TAG = Tag(
    name="Event offer prices", description="Endpoints to create and update price categories of an event."
)
EVENT_OFFER_DATES_TAG = Tag(
    name="Event offer dates",
    description="Endpoints to manage the dates of an event. The date of an event is composed of a price category and an actual date. \
        Hence for a given performance, you might have several dates (one per category).",
)

# PRODUCT TAGS
PRODUCT_OFFER_TAG = Tag(name="Product offer", description="Endpoints to manage product offers of a venue.")
IMAGE_TAG = Tag(name="Image")
PRODUCT_EAN_OFFER_TAG = Tag(
    name="Product offer bulk operations",
    description="Endpoints to create and get products usings European Article Number (EAN-13).",
)
OFFERER_VENUES_TAG = Tag(name="Offerer and Venues")
OFFER_ATTRIBUTES = Tag(name="Offer attributes")


# COLLECTIVE TAGS
COLLECTIVE_OFFERS = Tag(
    name="Collective offers",
    description='Endpoints to manage collective offers that are "bookable", not the one that are displayed in the showcase.',
)
COLLECTIVE_BOOKING = Tag(name="Collective booking")
COLLECTIVE_CATEGORIES = Tag(name="Collective categories")
COLLECTIVE_VENUES = Tag(name="Collective venues")
COLLECTIVE_EDUCATIONAL_DATA = Tag(name="Collective educational data")


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentication is necessary to use this API"),
    "HTTP_403": (None, "You do not have the necessary rights to use this API"),
    "HTTP_429": (None, "You have made too many requests. (**rate limit: 200 requests/minute**)"),
}

OPEN_API_TAGS = [
    # OFFERER VENUES
    OFFERER_VENUES_TAG,
    # EVENTS
    EVENT_OFFER_INFO_TAG,
    EVENT_OFFER_PRICES_TAG,
    EVENT_OFFER_DATES_TAG,
    # PRODUCTS
    PRODUCT_OFFER_TAG,
    PRODUCT_EAN_OFFER_TAG,
    # BOOKING
    BOOKING_TAG,
    # OFFERS ADDITIONNAL DATA
    IMAGE_TAG,
    OFFER_ATTRIBUTES,
    # COLLECTIVE
    COLLECTIVE_OFFERS,
    COLLECTIVE_BOOKING,
    COLLECTIVE_CATEGORIES,
    COLLECTIVE_VENUES,
    COLLECTIVE_EDUCATIONAL_DATA,
]

# DEPRECATED APIS TAGS
DEPRECATED_BOOKING_TOKEN = Tag(name="[Dépréciée] API Contremarque")
DEPRECATED_VENUES_STOCK = Tag(name="[Dépréciée] API stocks")


DEPRACTED_TAGS = [
    DEPRECATED_BOOKING_TOKEN,
    DEPRECATED_VENUES_STOCK,
]
