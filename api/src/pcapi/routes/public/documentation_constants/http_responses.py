# Success
HTTP_200_MESSAGE = "Your request was succesful."

HTTP_200_REQUEST_SUCCESSFUL = {"HTTP_200": (None, "Your request was succesful.")}
HTTP_204_VENUE_PROVIDER_EXTERNAL_URLS_UPDATE_SUCCESS = {
    "HTTP_204": (None, "This venue external urls have been successfully updated"),
}
HTTP_204_BOOKING_VALIDATION_SUCCESS = {
    "HTTP_204": (None, "This booking has been successfully validated"),
}
HTTP_204_BOOKING_CANCELLATION_SUCCESS = {
    "HTTP_204": (None, "This booking has been successfully cancelled"),
}
HTTP_204_BOOKING_VALIDATION_CANCELLATION_SUCCESS = {
    "HTTP_204": (None, "The booking's validation has been successfully cancelled"),
}

HTTP_204_COLLECTIVE_BOOKING_CANCELLATION_SUCCESS = {
    "HTTP_204": (None, "This collective booking has been successfully cancelled")
}

HTTP_204_COLLECTIVE_BOOKING_STATUS_UPDATE = {
    "HTTP_204": (None, "This collective booking's status has been successfully updated")
}

# Client errors
HTTP_400_BAD_REQUEST = {
    "HTTP_400": (None, "The request is invalid. The response body contains a list of errors."),
}
HTTP_401_UNAUTHENTICATED = {
    "HTTP_401": (None, "Authentication is necessary to use this API."),
}
HTTP_403_UNTHAUTHORIZED = {
    "HTTP_403": (None, "You do not have the necessary rights to use this API."),
}
HTTP_429_TOO_MANY_REQUESTS = {
    "HTTP_429": (None, "You have made too many requests. (**rate limit: 200 requests/minute**)"),
}

# Specific 404
HTTP_404_SOME_RESOURCE_NOT_FOUND = {
    "HTTP_404": (None, "Some resource has not been found."),
}
HTTP_404_VENUE_NOT_FOUND = {
    "HTTP_404": (None, "The venue could not found for your API key."),
}
HTTP_404_BOOKING_NOT_FOUND = {
    "HTTP_404": (None, "The booking could not be found."),
}
HTTP_404_EVENT_NOT_FOUND = {
    "HTTP_404": (None, "The event offer could not be found."),
}
HTTP_404_PRODUCT_NOT_FOUND = {
    "HTTP_404": (None, "The product offer could not be found."),
}
HTTP_404_OFFER_NOT_FOUND = {
    "HTTP_404": (None, "The offer could not be found."),
}
HTTP_404_COLLECTIVE_OFFER_NOT_FOUND = {
    "HTTP_404": (None, "The collective offer could not be found."),
}
HTTP_404_PRICE_CATEGORY_OR_EVENT_NOT_FOUND = {
    "HTTP_404": (None, "The event offer or the price category could not be found."),
}

# Specific 403
HTTP_403_BOOKING_REIMBURSED_OR_CONFIRMED_OR_NOT_USED = {
    "HTTP_403": (
        None,
        "You are not authorized to perform this action because the booking has either been reimbursed, confirmed or not used.",
    )
}
HTTP_403_COLLECTIVE_OFFER_INACTIVE_INSTITUTION = {
    "HTTP_403": (None, "The educational institution is not active."),
}
HTTP_403_COLLECTIVE_OFFER_INSUFFICIENT_RIGHTS = {
    "HTTP_403": (None, "You don't have enough rights to access or edit the collective offer"),
}

HTTP_403_COLLECTIVE_BOOKING_STATUS_UPDATE_REFUSED = {
    "HTTP_403": (None, "Collective booking status updated has been refused"),
}

# Specific 410
HTTP_410_BOOKING_CANCELED_OR_VALIDATED = {
    "HTTP_410": (None, "You cannot perform this action because the booking has either been validated or canceled.")
}

# All our public APIs require authentication and implement rate limiting.
HTTP_40X_SHARED_BY_API_ENDPOINTS = HTTP_401_UNAUTHENTICATED | HTTP_429_TOO_MANY_REQUESTS
