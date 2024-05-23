# HIGH LEVEL INFORMATION
PUBLIC_API_DESCRIPTION = """
This the documentation of the Pass Culture public REST API.

# Important notice
- Since January 2023, rate limiting has been implemented on the Pass Culture API.
  You are limited to **200 requests/minute** per API key.
  Once this limit reached, you will received a `429 Too Many Requests` error message. You will then need to back down.
- Dates of event offers are stored in the **UTC format** to be able to format them correctly, according to the user timezone, in our application interface.
- Any non-blank field sent using a `PATCH` method will be considered as changed, even if the new value is equal to old value.
  _For example, if you update the stock of an event, you **should not resend the `beginningDate`** if it has not changed because, otherwise it is going to trigger the reschedule process on our side._

# Authentication
The authentication system on Pass Culture API is using an API Key. For each of your requests, you should put your API key in the authorization header of the request following the `Bearer`pattern.
That is to say that in your request headers you should have a line that look like this : `Authorization: Bearer {you_api_key}` (**⚠️ Make sure to use the right API key for the right environment**)
An API key is linked to a provider and will give you access to the venues linked to this provider by the offerers.
"""


# FIELDS DESCRIPTIONS
OFFER_STATUS_FIELD_DESCRIPTION = """
**Offer status:**

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
