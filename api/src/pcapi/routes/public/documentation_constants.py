from spectree import Tag


# BOOKING_TAGS
BOOKING_TAG = Tag(name="Booking")

# EVENT TAGS
EVENT_OFFER_INFO_TAG = Tag(
    name="Event offer", description="All the routes to handle event offers data (except prices and dates)"
)
EVENT_OFFER_PRICES_TAG = Tag(name="Event offer prices")
EVENT_OFFER_DATES_TAG = Tag(name="Event offer dates")

# PRODUCT TAGS
PRODUCT_OFFER_TAG = Tag(name="Product offer")
IMAGE_TAG = Tag(name="Image")
PRODUCT_EAN_OFFER_TAG = Tag(name="Bulk product offer operation")
OFFERER_VENUES_TAG = Tag(name="Offerer and Venues")
OFFER_ATTRIBUTES = Tag(name="Offer attributes")


# COLLECTIVE TAGS
COLLECTIVE_OFFERS = Tag(name="Collective offers")
COLLECTIVE_BOOKING = Tag(name="Collective booking")
COLLECTIVE_CATEGORIES = Tag(name="Collective categories")
COLLECTIVE_VENUES = Tag(name="Collective venues")
COLLECTIVE_EDUCATIONAL_DATA = Tag(name="Collective educational data")


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentication is necessary to use this API"),
    "HTTP_403": (None, "You do not have the necessary rights to use this API"),
}

OPEN_API_TAGS = [
    # EVENTS
    OFFERER_VENUES_TAG,
    EVENT_OFFER_INFO_TAG,
    EVENT_OFFER_DATES_TAG,
    EVENT_OFFER_PRICES_TAG,
    OFFER_ATTRIBUTES,
    # BOOKING
    BOOKING_TAG,
    # PRODUCTS
    PRODUCT_OFFER_TAG,
    IMAGE_TAG,
    PRODUCT_EAN_OFFER_TAG,
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
