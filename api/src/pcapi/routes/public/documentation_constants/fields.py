import datetime

from dateutil import relativedelta

from pcapi.utils import date as date_utils


_next_month = datetime.datetime.utcnow().replace(hour=12, minute=0, second=0) + relativedelta.relativedelta(months=1)
_paris_tz_next_month = date_utils.utc_datetime_to_department_timezone(_next_month, "75")


class VENUE_ID_FIELD_DATA:
    example = 1234
    description = "Venue Id. The venues list is available on [**this endpoint (`Get offerer venues`)**](#tag/Offerer-and-Venues/operation/GetOffererVenues)"


class DURATION_MINUTES_FIELD_DATA:
    description = "Event duration in minutes"
    example = 60
    alias = "eventDuration"


# Image Fields
class IMAGE_CREDIT_FIELD_DATA:
    description = "Image owner or author"
    example = "Jane Doe"


class IMAGE_FILE_FIELD_DATA:
    description = "Image file encoded in base64 string. Image format must be PNG or JPEG. Size must be between 400x600 and 800x1200 pixels. Aspect ratio must be 2:3 (portrait format)."
    example = "iVBORw0KGgoAAAANSUhEUgAAAhUAAAMgCAAAAACxT88IAAABImlDQ1BJQ0MgcHJvZmlsZQAAKJGdkLFKw1AUhr+0oiKKg6IgDhlcO5pFB6tCKCjEWMHqlCYpFpMYkpTiG/gm+jAdBMFXcFdw9r/RwcEs3nD4Pw7n/P+9gZadhGk5dwBpVhWu3x1cDq7shTfa+lbZZC8Iy7zreSc0ns9XLKMvHePVPPfnmY/iMpTOVFmYFxVY+2JnWuWGVazf9v0j8YPYjtIsEj+Jd6I0Mmx2/TSZhD+e5jbLcXZxbvqqbVx6nOJhM2TCmISKjjRT5xiHXalLQcA9JaE0IVZvqpmKG1EpJ5dDUV+k2zTkbdV5nlKG8hjLyyTckcrT5GH+7/fax1m9aW3M8qAI6lZb1RqN4P0RVgaw9gxL1w1Zi7/f1jDj1DP/fOMXG7hQfuNVil0AAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfnAwMPGDrdy1JyAAABtElEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8GaFGgABH6N7kwAAAABJRU5ErkJggg=="


class AUDIO_DISABILITY_FIELD_DATA:
    description = "Is accessible for people with hearing disability"
    example = True


class MENTAL_DISABILITY_FIELD_DATA:
    description = "Is accessible for people with mental disability"
    example = True


class MOTOR_DISABILITY_FIELD_DATA:
    description = "Is accessible for people with motor disability"
    example = True


class VISUAL_DISABILITY_FIELD_DATA:
    description = "Is accessible for people with visual disability"
    example = True


# Collective offer specific fields
class COLLECTIVE_OFFER_NAME:
    description = "Collective offer name"
    example = "Atelier de peinture"


class COLLECTIVE_OFFER_DESCRIPTION:
    description = "Collective offer description"
    example = "Atelier de peinture à la gouache pour élèves de 5ème"


class COLLECTIVE_OFFER_SUBCATEGORY_ID_FIELD_DATA:
    description = "Event subcategory id"
    example = "FESTIVAL_MUSIQUE"


class COLLECTIVE_OFFER_FORMATS_FIELD_DATA:
    description = "Educational Formats"
    example = ["Atelier de pratique"]


class COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA:
    description = "Recipient emails for notifications about bookings, cancellations, etc."
    example = ["some@email.com", "some.other@email.com"]


class COLLECTIVE_OFFER_CONTACT_EMAIL_FIELD_DATA:
    example = "somebody.tocontact@gmail.com"
    description = "Email of the person to contact if there is an issue with the offer."


class COLLECTIVE_OFFER_CONTACT_PHONE_FIELD_DATA:
    example = "somebody.tocontact@gmail.com"
    description = "Phone of the person to contact if there is an issue with the offer."


class COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS_FIELD_DATA:
    example = [1, 2]
    description = "Educational domains ids linked to the offer. Those domains are available on **[this endpoint (`Get the eductional domains`)](#tag/Collective-educational-data/operation/ListEducationalDomains)**"


class COLLECTIVE_OFFER_STUDENT_LEVELS_FIELD_DATA:
    description = "Student levels that can take pat to the collective offer. The student levels are available on [**this endpoint (`Get student levels eligible for collective offers`)**](#tag/Collective-educational-data/operation/ListStudentsLevels)"
    example = ["GENERAL2", "GENERAL1", "GENERAL0"]


class COLLECTIVE_OFFER_IS_ACTIVE_FIELD_DATA:
    description = "Is your offer active"
    example = True


class COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID_FIELD_DATA:
    description = "Id of the national program linked to your offer. The national programs list can be found on **[this endpoint (`Get all known national programs`)](#tag/Collective-educational-data/operation/GetNationalPrograms)**"
    example = 123456


class COLLECTIVE_OFFER_BEGINNING_DATETIME_FIELD_DATA:
    description = "Collective offer beginning datetime. It cannot be a date in the past. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime)."
    example = _paris_tz_next_month.isoformat(timespec="seconds")


class COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME_FIELD_DATA:
    description = "Booking limit datetime. It must be anterior to the `beginning_datetime`. The expected format is **[ISO 8601](https://fr.wikipedia.org/wiki/ISO_8601)** (standard format for timezone aware datetime)."
    example = _paris_tz_next_month.isoformat(timespec="seconds")


class COLLECTIVE_OFFER_TOTAL_PRICE_FIELD_DATA:
    example = 100.00
    description = "Collective offer price (in €)"


class COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD_DATA:
    example = 10
    description = "Number of tickets for your collective offer"


class COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD_DATA:
    description = "The explanation of the offer price"
    example = "10 tickets x 10 € = 100 €"


class COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD_DATA:
    description = "Pass Culture id of the educational institution using this offer. The institions can be found on **[this endpoint (`Get all educational institutions`)](#tag/Collective-educational-data/operation/ListEducationalInstitutions)**"
    example = 1234


class COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD_DATA:
    description = "Institution id of the educational institution using this offer. The institions can be found on **[this endpoint (`Get all educational institutions`)](#tag/Collective-educational-data/operation/ListEducationalInstitutions)**"
    example = "uai"
