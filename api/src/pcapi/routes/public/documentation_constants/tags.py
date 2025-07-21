from spectree import Tag


# BOOKING
BOOKINGS = Tag(name="Bookings", description="Endpoints to manage the bookings of an offer (event and product).")

# ADDRESSES
ADDRESSES = Tag(
    name="Addresses",
    description="Endpoints for managing addresses, allowing you to specify an offer location that differs from the venue's location.",
)

# EVENT OFFERS
EVENT_OFFERS = Tag(
    name="Event Offers", description="Endpoints to manage event offers data of a venue (except prices and dates)."
)
EVENT_OFFER_PRICES = Tag(
    name="Event Offer Price Categories", description="Endpoints to create and update price categories of an event."
)
EVENT_OFFER_STOCKS = Tag(
    name="Event Offer Stocks",
    description="Endpoints to manage events stocks. An event stock has a price category, a date and a quantity. \
        Hence for a given performance date, you might have several stocks (one per category).",
)

# PRODUCT OFFERS
PRODUCT_OFFERS = Tag(name="Product Offers", description="Endpoints to manage product offers of a venue.")
IMAGE = Tag(name="Images")
PRODUCT_EAN_OFFERS = Tag(
    name="Product Offer Bulk Operations",
    description="Endpoints to create and get products usings European Article Number (EAN-13).",
)
PROVIDERS = Tag(name="Providers")
VENUES = Tag(name="Venues")
OFFER_ATTRIBUTES = Tag(name="Offer Attributes")


# COLLECTIVE OFFERS
COLLECTIVE_OFFERS = Tag(
    name="Collective Offers",
    description='Endpoints to manage collective offers that are "bookable", not those that are displayed in the showcase.',
)
COLLECTIVE_BOOKINGS = Tag(name="Collective Bookings")
COLLECTIVE_OFFER_ATTRIBUTES = Tag(name="Collective Offer Attributes")

# COLLECTIVE BOOKINGS ADAGE MOCK
COLLECTIVE_ADAGE_MOCK = Tag(name="Adage Mock (Collective Bookings)")

# COLLECTIVE OFFERS --- Deprecated
DEPRECATED_COLLECTIVE_VENUES = Tag(name="[DEPRECATED] Collective venues")


OPEN_API_TAGS = [
    # PROVIDERS
    PROVIDERS,
    # VENUES
    VENUES,
    # ADDRESSES,
    ADDRESSES,
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
]

# DEPRECATED APIS
DEPRECATED_BOOKING_TOKEN = Tag(name="[Dépréciée] API Contremarque")


DEPRECATED_COLLECTIVE_TAGS = [
    DEPRECATED_COLLECTIVE_VENUES,
]
