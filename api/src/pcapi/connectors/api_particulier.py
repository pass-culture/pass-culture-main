import datetime
import email.utils
import enum
import functools
import logging
import time
import typing

from pydantic import BaseModel
from pydantic import field_validator

from pcapi import settings
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils
from pcapi.utils import rate_limit as rate_limit_utils
from pcapi.utils import requests
from pcapi.utils.redis import get_redis_client
from pcapi.utils.requests import Response


logger = logging.getLogger(__name__)


QUOTIENT_FAMILIAL_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/quotient_familial/identite"
AAH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_adulte_handicape/identite"
AEEH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_enfant_handicape/identite"

RATE_LIMIT_KEY = "api_particulier"
RATE_LIMIT_TIME_WINDOW_SIZE = 60  # seconds
# set when API Particulier rate limits us, so that every worker stops calling them until they accept our calls again
RATE_LIMIT_LOCK_KEY = f"pcapi:rate_limit:{RATE_LIMIT_KEY}:lock"
# `RateLimit-Reset` is documented as a number of seconds, but some gouv.fr APIs send a unix timestamp instead
_UNIX_TIMESTAMP_THRESHOLD = 1_000_000_000


class ParticulierApiException(Exception):
    def __init__(
        self,
        message: str = "",
        *,
        status_code: int,
        error_code: str | None = None,
        error_title: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_title = error_title
        # when set, tells the caller (usually a celery task) how many seconds it should wait before retrying
        self.retry_after = retry_after


class ParticulierApiForbidden(ParticulierApiException):
    pass


class ParticulierApiApplicationNotFound(ParticulierApiException):
    pass


class ParticulierApiPersonNotFound(ParticulierApiException):
    pass


class ParticulierApiUnavailable(ParticulierApiException):
    pass


class ParticulierApiRequestConflict(ParticulierApiException):
    pass


class ParticulierApiQueryError(ParticulierApiException):
    pass


class ParticulierApiRateLimitExceeded(ParticulierApiException):
    pass


def rate_limited[**P, T](func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    """
    Client side rate limit, shared by every worker, so that we stop calling API Particulier
    before they start rejecting our calls, and stop until `Retry-After` passes once they do.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        remaining_lock_seconds = _get_rate_limit_lock_ttl()
        if remaining_lock_seconds:
            raise ParticulierApiRateLimitExceeded(
                "API Particulier is rate limiting us", status_code=429, retry_after=remaining_lock_seconds
            )

        try:
            with rate_limit_utils.rate_limit(
                key=RATE_LIMIT_KEY,
                time_window_size=RATE_LIMIT_TIME_WINDOW_SIZE,
                max_per_time_window=settings.PARTICULIER_API_RATE_LIMIT_THRESHOLD,
            ):
                return func(*args, **kwargs)
        except rate_limit_utils.RateLimitedError as e:
            retry_after = _get_seconds_before_next_time_window()
            logger.warning(
                "API Particulier client side rate limit reached",
                extra={"limit": e.max_per_time_window, "current": e.current, "retry_after": retry_after},
            )
            raise ParticulierApiRateLimitExceeded(
                "client side rate limit reached", status_code=429, retry_after=retry_after
            ) from e
        except ParticulierApiRateLimitExceeded as e:
            # they rejected that call: every other call is going to be rejected as well until `Retry-After` passes
            e.retry_after = max(1, e.retry_after or _get_seconds_before_next_time_window())
            _lock_until_rate_limit_reset(e.retry_after)
            raise

    return wrapper


def _get_rate_limit_lock_ttl() -> int:
    # `ttl` returns a negative value when the key has no expiry (-1) or does not exist (-2)
    return max(0, get_redis_client().ttl(RATE_LIMIT_LOCK_KEY))


def _lock_until_rate_limit_reset(retry_after: int) -> None:
    get_redis_client().set(RATE_LIMIT_LOCK_KEY, "1", ex=retry_after)


def _get_seconds_before_next_time_window() -> int:
    now = int(time.time())
    next_time_window_start = (now // RATE_LIMIT_TIME_WINDOW_SIZE + 1) * RATE_LIMIT_TIME_WINDOW_SIZE
    return max(1, next_time_window_start - now)


def _get_retry_after(response: Response) -> int | None:
    """
    API Particulier sends `Retry-After`, along with `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`,
    when it rate limits us. `Retry-After` is either a number of seconds or an HTTP date.
    """
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0, int(retry_after))
        except ValueError:
            pass

        try:
            retry_date = email.utils.parsedate_to_datetime(retry_after)
        except (TypeError, ValueError):
            retry_date = None

        if retry_date:
            if retry_date.tzinfo is None:
                retry_date = retry_date.replace(tzinfo=datetime.UTC)
            return max(0, int((retry_date - datetime.datetime.now(datetime.UTC)).total_seconds()))

    rate_limit_reset = response.headers.get("RateLimit-Reset")
    if rate_limit_reset:
        try:
            seconds_before_reset = int(rate_limit_reset)
        except ValueError:
            return None

        if seconds_before_reset > _UNIX_TIMESTAMP_THRESHOLD:
            seconds_before_reset -= int(time.time())
        return max(0, seconds_before_reset)

    return None


class ApiParticulierPerson(BaseModel):
    nom_naissance: str | None = None
    nom_usage: str | None = None
    prenoms: str | None = None
    date_naissance: datetime.date | None = None
    sexe: users_models.GenderEnum | None = None

    @field_validator("sexe", mode="before")
    @classmethod
    def parse_gender(cls, gender: typing.Any) -> users_models.GenderEnum | None:
        if isinstance(gender, str):
            try:
                return users_models.GenderEnum[gender]
            except KeyError:
                return users_models.GenderEnum(gender)
        if isinstance(gender, users_models.GenderEnum):
            return gender
        if gender is None:
            return None

        raise ValueError(f"Unexpected {gender = } given")


class QuotientFamilial(BaseModel):
    fournisseur: str
    valeur: int
    annee: int
    mois: int
    annee_calcul: int
    mois_calcul: int


class QuotientFamilialData(BaseModel):
    allocataires: list[ApiParticulierPerson]
    enfants: list[ApiParticulierPerson]
    quotient_familial: QuotientFamilial


class QuotientFamilialResponse(BaseModel):
    data: QuotientFamilialData


@rate_limited
def get_quotient_familial(
    custodian: bonus_schemas.BonusCreditPerson, at_date: datetime.date | None = None
) -> QuotientFamilialResponse:
    """
    Get the Quotient Familial from a tax household, using a custodian personal information.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Quotient-familial-CAF-and-MSA
    """
    country_insee_code = custodian.birth_country_cog_code
    city_insee_code = custodian.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": custodian.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in custodian.first_names],
        "nomUsage": custodian.common_name.upper() if custodian.common_name else None,
        "anneeDateNaissance": custodian.birth_date.year,
        "moisDateNaissance": custodian.birth_date.month,
        "jourDateNaissance": custodian.birth_date.day,
        "sexeEtatCivil": custodian.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": custodian.birth_city,
        "annee": at_date.year if at_date else None,
        "mois": at_date.month if at_date else None,
    }
    response = requests.get(
        QUOTIENT_FAMILIAL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "quotient familial")

    return QuotientFamilialResponse.model_validate(response.json())


class DisabledAdultAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is recipient to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not recipient, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    est_beneficiaire: bool
    date_debut_droit: datetime.date | None


class DisabledAdultAllowanceResponse(BaseModel):
    data: DisabledAdultAllowanceData


@rate_limited
def get_disabled_adult_allowance(person: bonus_schemas.BonusCreditPerson) -> DisabledAdultAllowanceResponse:
    """
    Get whether the person benefits from the disabled adult allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-Adulte-Handicape-(AAH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": person.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in person.first_names],
        "nomUsage": person.common_name.upper() if person.common_name else None,
        "anneeDateNaissance": person.birth_date.year,
        "moisDateNaissance": person.birth_date.month,
        "jourDateNaissance": person.birth_date.day,
        "sexeEtatCivil": person.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": person.birth_city,
    }
    response = requests.get(
        AAH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "aah")

    return DisabledAdultAllowanceResponse.model_validate(response.json())


class DisabledChildEducationAllowanceStatus(enum.StrEnum):
    RECIPIENT = "allocataire"
    RIGHT_OPENING = "ouvrant_droit"
    NON_RECIPIENT = "non_beneficiaire"


class DisabledChildEducationAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is recipient to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not recipient, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    status: DisabledChildEducationAllowanceStatus
    date_debut_droit: datetime.date | None


class DisabledChildEducationAllowanceResponse(BaseModel):
    data: DisabledChildEducationAllowanceData


@rate_limited
def get_disabled_child_education_allowance(
    person: bonus_schemas.BonusCreditPerson,
) -> DisabledChildEducationAllowanceResponse:
    """
    Get whether the person benefits from the disabled child education allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-d'Education-de-l'Enfant-Handicape-(AEEH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": person.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in person.first_names],
        "nomUsage": person.common_name.upper() if person.common_name else None,
        "anneeDateNaissance": person.birth_date.year,
        "moisDateNaissance": person.birth_date.month,
        "jourDateNaissance": person.birth_date.day,
        "sexeEtatCivil": person.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": person.birth_city,
    }
    response = requests.get(
        AEEH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "aeeh")

    return DisabledChildEducationAllowanceResponse.model_validate(response.json())


def _raise_for_status(response: Response, endpoint_label: str) -> None:
    if response.ok:
        return

    try:
        api_particulier_error = response.json()["errors"][0]
        error_code, error_title = api_particulier_error["code"], api_particulier_error["title"]
        message = f"{endpoint_label} {int(response.status_code)} error_code={error_code} error_title={error_title}"
    except (ValueError, KeyError):  # JSON decode error
        error_code, error_title = None, None
        message = f"{endpoint_label} unparsable error"

    retry_after = _get_retry_after(response)

    ExceptionClass = ParticulierApiException
    if response.status_code == 403:
        ExceptionClass = ParticulierApiForbidden
    elif response.status_code == 404:
        # the person was found, but no application was found
        ExceptionClass = ParticulierApiApplicationNotFound
    elif response.status_code == 409:
        ExceptionClass = ParticulierApiRequestConflict
    elif response.status_code == 422:
        # what we usually think of 404 not found: either nobody or more than one person was found
        ExceptionClass = ParticulierApiPersonNotFound
    elif response.status_code == 429:
        ExceptionClass = ParticulierApiRateLimitExceeded
        logger.warning(
            "API Particulier rate limit exceeded",
            extra={
                "endpoint": endpoint_label,
                "limit": response.headers.get("RateLimit-Limit"),
                "remaining": response.headers.get("RateLimit-Remaining"),
                "reset": response.headers.get("RateLimit-Reset"),
                "retry_after": retry_after,
            },
        )
    elif response.status_code // 100 == 4:
        ExceptionClass = ParticulierApiQueryError
    elif response.status_code // 100 == 5:
        ExceptionClass = ParticulierApiUnavailable

    raise ExceptionClass(
        message,
        status_code=response.status_code,
        error_code=error_code,
        error_title=error_title,
        retry_after=retry_after,
    )
