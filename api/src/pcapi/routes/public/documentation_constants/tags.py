from spectree import Tag


# BOOKING
BOOKINGS = Tag(name="Bookings", description="Endpoints to manage the bookings of an offer (event and product).")

# EVENT OFFERS
EVENT_OFFERS = Tag(
    name="Event offers", description="Endpoints to manage event offers data of a venue (except prices and dates)."
)
EVENT_OFFER_PRICES = Tag(
    name="Event offer prices", description="Endpoints to create and update price categories of an event."
)
EVENT_OFFER_STOCKS = Tag(
    name="Event offer stocks",
    description="Endpoints to manage events stocks. An event stock has a price category, a date and a quantity. \
        Hence for a given performance date, you might have several stocks (one per category).",
)

# PRODUCT OFFERS
PRODUCT_OFFERS = Tag(name="Product offers", description="Endpoints to manage product offers of a venue.")
IMAGE = Tag(name="Images")
PRODUCT_EAN_OFFERS = Tag(
    name="Product offer bulk operations",
    description="Endpoints to create and get products usings European Article Number (EAN-13).",
)
PROVIDERS = Tag(name="Providers")
VENUES = Tag(name="Venues")
OFFER_ATTRIBUTES = Tag(name="Offer attributes")


# COLLECTIVE OFFERS
COLLECTIVE_OFFERS = Tag(
    name="Collective offers",
    description='Endpoints to manage collective offers that are "bookable", not those that are displayed in the showcase.',
)
COLLECTIVE_BOOKINGS = Tag(name="Collective bookings")
COLLECTIVE_OFFER_ATTRIBUTES = Tag(name="Collective offer attributes")

# COLLECTIVE OFFERS --- Deprecated
COLLECTIVE_CATEGORIES = Tag(name="[DEPRECATED] Collective categories")
COLLECTIVE_VENUES = Tag(name="[DEPRECATED] Collective venues")


OPEN_API_TAGS = [
    # PROVIDERS
    PROVIDERS,
    # VENUES
    VENUES,
    # PRODUCTS
    PRODUCT_EAN_OFFERS,
    PRODUCT_OFFERS,
    # EVENTS
    EVENT_OFFERS,
    EVENT_OFFER_PRICES,
    EVENT_OFFER_STOCKS,
    # OFFERS ADDITIONAL DATA
    IMAGE,
    OFFER_ATTRIBUTES,
    # BOOKINGS
    BOOKINGS,
    # COLLECTIVE
    COLLECTIVE_OFFERS,
    COLLECTIVE_BOOKINGS,
    COLLECTIVE_OFFER_ATTRIBUTES,
    # COLLECTIVE DEPRECATED ENDPOINTS
    COLLECTIVE_CATEGORIES,
    COLLECTIVE_VENUES,
]

# DEPRECATED APIS
DEPRECATED_BOOKING_TOKEN = Tag(name="[Dépréciée] API Contremarque")
DEPRECATED_VENUES_STOCK = Tag(name="[Dépréciée] API stocks")


DEPRECATED_TAGS = [
    DEPRECATED_BOOKING_TOKEN,
    DEPRECATED_VENUES_STOCK,
]
