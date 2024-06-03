import datetime

from dateutil import relativedelta
from pydantic.v1 import Field

from pcapi.routes.public.documentation_constants import descriptions
from pcapi.utils import date as date_utils


_next_month = datetime.datetime.utcnow().replace(hour=12, minute=0, second=0) + relativedelta.relativedelta(months=1)
_paris_tz_next_month = date_utils.utc_datetime_to_department_timezone(_next_month, "75")


VENUE_ID = Field(
    example=1234,
    description="Venue Id. The venues list is available on [**this endpoint (`Get offerer venues`)**](#tag/Offerer-and-Venues/operation/GetOffererVenues)",
)
DURATION_MINUTES = Field(
    description="Event duration in minutes",
    example=60,
)
OFFER_STATUS = Field(description=descriptions.OFFER_STATUS_FIELD_DESCRIPTION, example="ACTIVE")


PERIOD_BEGINNING_DATE = Field(
    description="Period beginning date. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
    example="2024-03-03T13:00:00+02:00",
)
PERIOD_ENDING_DATE = Field(
    description="Period ending date. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
    example="2024-05-10T15:00:00+02:00",
)


# Image Fields
IMAGE_CREDIT = Field(description="Image owner or author", example="Jane Doe")
IMAGE_FILE = Field(
    description="Image file encoded in base64 string. Image format must be PNG or JPEG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format).",
    example="iVBORw0KGgoAAAANSUhEUgAAAhUAAAMgCAAAAACxT88IAAABImlDQ1BJQ0MgcHJvZmlsZQAAKJGdkLFKw1AUhr+0oiKKg6IgDhlcO5pFB6tCKCjEWMHqlCYpFpMYkpTiG/gm+jAdBMFXcFdw9r/RwcEs3nD4Pw7n/P+9gZadhGk5dwBpVhWu3x1cDq7shTfa+lbZZC8Iy7zreSc0ns9XLKMvHePVPPfnmY/iMpTOVFmYFxVY+2JnWuWGVazf9v0j8YPYjtIsEj+Jd6I0Mmx2/TSZhD+e5jbLcXZxbvqqbVx6nOJhM2TCmISKjjRT5xiHXalLQcA9JaE0IVZvqpmKG1EpJ5dDUV+k2zTkbdV5nlKG8hjLyyTckcrT5GH+7/fax1m9aW3M8qAI6lZb1RqN4P0RVgaw9gxL1w1Zi7/f1jDj1DP/fOMXG7hQfuNVil0AAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfnAwMPGDrdy1JyAAABtElEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8GaFGgABH6N7kwAAAABJRU5ErkJggg==",
)

# Disability fields
AUDIO_DISABILITY = Field(description="Is accessible for people with hearing disability", example=True)
MENTAL_DISABILITY = Field(description="Is accessible for people with mental disability", example=True)
MOTOR_DISABILITY = Field(description="Is accessible for people with motor disability", example=True)
VISUAL_DISABILITY = Field(description="Is accessible for people with visual disability", example=True)
AUDIO_DISABILITY_WITH_DEFAULT = Field(
    False, description="Is accessible for people with hearing disability", example=True
)
MENTAL_DISABILITY_WITH_DEFAULT = Field(
    False, description="Is accessible for people with mental disability", example=True
)
MOTOR_DISABILITY_WITH_DEFAULT = Field(False, description="Is accessible for people with motor disability", example=True)
VISUAL_DISABILITY_WITH_DEFAULT = Field(
    False, description="Is accessible for people with visual disability", example=True
)

# Collective offer specific fields
COLLECTIVE_OFFER_NAME = Field(description="Collective offer name", example="Atelier de peinture")
COLLECTIVE_OFFER_DESCRIPTION = Field(
    description="Collective offer description", example="Atelier de peinture à la gouache pour élèves de 5ème"
)
COLLECTIVE_OFFER_SUBCATEGORY_ID = Field(description="Event subcategory id", example="FESTIVAL_MUSIQUE")
COLLECTIVE_OFFER_FORMATS = Field(description="Educational Formats", example=["Atelier de pratique"])
COLLECTIVE_OFFER_BOOKING_EMAILS = Field(
    description="Recipient emails for notifications about bookings, cancellations, etc.",
    example=["some@email.com", "some.other@email.com"],
)
COLLECTIVE_OFFER_CONTACT_EMAIL = Field(
    example="somebody.tocontact@gmail.com",
    description="Email of the person to contact if there is an issue with the offer.",
)
COLLECTIVE_OFFER_CONTACT_PHONE = Field(
    example="somebody.tocontact@gmail.com",
    description="Phone of the person to contact if there is an issue with the offer.",
)
COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS = Field(
    example=[1, 2],
    description="Educational domains ids linked to the offer. Those domains are available on **[this endpoint (`Get the eductional domains`)](#tag/Collective-educational-data/operation/ListEducationalDomains)**",
)
COLLECTIVE_OFFER_STUDENT_LEVELS = Field(
    description="Student levels that can take pat to the collective offer. The student levels are available on [**this endpoint (`Get student levels eligible for collective offers`)**](#tag/Collective-educational-data/operation/ListStudentsLevels)",
    example=["GENERAL2", "GENERAL1", "GENERAL0"],
)
COLLECTIVE_OFFER_IS_ACTIVE = Field(description="Is your offer active", example=True)
COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID = Field(
    description="Id of the national program linked to your offer. The national programs list can be found on **[this endpoint (`Get all known national programs`)](#tag/Collective-educational-data/operation/GetNationalPrograms)**",
    example=123456,
)
COLLECTIVE_OFFER_BEGINNING_DATETIME = Field(
    description="Collective offer beginning datetime. It cannot be a date in the past. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
    example=_paris_tz_next_month.isoformat(timespec="seconds"),
)
COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME = Field(
    description="Booking limit datetime. It must be anterior to the `beginning_datetime`. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime).",
    example=_paris_tz_next_month.isoformat(timespec="seconds"),
)
COLLECTIVE_OFFER_TOTAL_PRICE = Field(example=100.00, description="Collective offer price (in €)")
COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD = Field(example=10, description="Number of tickets for your collective offer")
COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD = Field(
    description="The explanation of the offer price", example="10 tickets x 10 € = 100 €"
)
COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD = Field(
    description="Pass Culture id of the educational institution using this offer. The institions can be found on **[this endpoint (`Get all educational institutions`)](#tag/Collective-educational-data/operation/ListEducationalInstitutions)**",
    example=1234,
)
COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD = Field(
    description="Institution id of the educational institution using this offer. The institions can be found on **[this endpoint (`Get all educational institutions`)](#tag/Collective-educational-data/operation/ListEducationalInstitutions)**",
    example="uai",
)
