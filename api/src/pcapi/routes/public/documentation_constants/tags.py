from spectree import Tag


# BOOKING_TAGS
BOOKINGS_TAG = Tag(name="Bookings", description="Endpoints to manage the bookings of an offer (event and product).")

# EVENT TAGS
EVENT_OFFERS_TAG = Tag(
    name="Event offers", description="Endpoints to manage event offers data of a venue (except prices and dates)."
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
PRODUCT_OFFERS_TAG = Tag(name="Product offers", description="Endpoints to manage product offers of a venue.")
IMAGE_TAG = Tag(name="Images")
PRODUCT_EAN_OFFERS_TAG = Tag(
    name="Product offer bulk operations",
    description="Endpoints to create and get products usings European Article Number (EAN-13).",
)
VENUES_TAG = Tag(name="Venues")
OFFER_ATTRIBUTES = Tag(name="Offer attributes")


# COLLECTIVE TAGS
COLLECTIVE_OFFERS_TAG = Tag(
    name="Collective offers",
    description='Endpoints to manage collective offers that are "bookable", not those that are displayed in the showcase.',
)
COLLECTIVE_BOOKINGS_TAG = Tag(name="Collective bookings")
COLLECTIVE_OFFER_ATTRIBUTES_TAG = Tag(name="Collective offer attributes")

# COLLECTIVE TAGS --- Deprecated
COLLECTIVE_CATEGORIES_TAG = Tag(name="[DEPRECATED] Collective categories")
COLLECTIVE_VENUES_TAG = Tag(name="[DEPRECATED] Collective venues")


OPEN_API_TAGS = [
    # OFFERER VENUES
    VENUES_TAG,
    # PRODUCTS
    PRODUCT_EAN_OFFERS_TAG,
    PRODUCT_OFFERS_TAG,
    # EVENTS
    EVENT_OFFERS_TAG,
    EVENT_OFFER_PRICES_TAG,
    EVENT_OFFER_DATES_TAG,
    # OFFERS ADDITIONAL DATA
    IMAGE_TAG,
    OFFER_ATTRIBUTES,
    # BOOKINGS
    BOOKINGS_TAG,
    # COLLECTIVE
    COLLECTIVE_OFFERS_TAG,
    COLLECTIVE_BOOKINGS_TAG,
    COLLECTIVE_OFFER_ATTRIBUTES_TAG,
    # COLLECTIVE DEPRECATED ENDPOINTS
    COLLECTIVE_CATEGORIES_TAG,
    COLLECTIVE_VENUES_TAG,
]

# DEPRECATED APIS TAGS
DEPRECATED_BOOKING_TOKEN_TAG = Tag(name="[Dépréciée] API Contremarque")
DEPRECATED_VENUES_STOCK_TAG = Tag(name="[Dépréciée] API stocks")


DEPRACTED_TAGS = [
    DEPRECATED_BOOKING_TOKEN_TAG,
    DEPRECATED_VENUES_STOCK_TAG,
]
