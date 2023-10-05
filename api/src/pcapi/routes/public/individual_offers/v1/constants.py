from pcapi.utils import image_conversion


# Event API tags
EVENT_OFFER_INFO_TAG = "Event offer main information (except prices and dates)"
EVENT_OFFER_PRICES_TAG = "Event offer prices"
EVENT_OFFER_DATES_TAG = "Event offer dates"


# Procuct API tags
PRODUCT_OFFER_TAG = "Product offer"
PRODUCT_EAN_OFFER_TAG = "Bulk product offer operation"
OFFERER_VENUES_TAG = "Offerer and Venues"
OFFER_ATTRIBUTES = "Offer attributes"

# Booking API tags
BOOKING_TAG = "Booking"


# Image settings
MIN_IMAGE_WIDTH = 400
MAX_IMAGE_WIDTH = 800
MIN_IMAGE_HEIGHT = 600
MAX_IMAGE_HEIGHT = 1200
ASPECT_RATIO = image_conversion.ImageRatio.PORTRAIT

BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentication is necessary to use this API"),
    "HTTP_403": (None, "You do not have the necessary rights to use this API"),
}
