"""
Wrapper around the API Particulier connector that allows configuration of their
reponse through config BeneficiaryFraudChecks.

The API Particulier staging dataset is documented at
https://github.com/datagouv/apistration/tree/develop/mocks/payloads/
"""

import datetime

from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils


DATA_PROVIDER_ERROR = bonus_schemas.BonusCreditPerson(
    last_name="delanoue",
    first_names=["jean-marie"],
    birth_date=datetime.date(2002, 12, 5),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
PERSON_NOT_FOUND = bonus_schemas.BonusCreditPerson(
    last_name="a_very_very_very_very_very_very_very_very_very_very_ver_very_very_very_very_very_long_name",
    common_name=None,
    first_names=["877khkshkq+"],
    birth_date=datetime.date(1982, 12, 7),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code="B&543",
    birth_city_cog_code="AAAAA",
)
QF_APPLICATION_NOT_FOUND = bonus_schemas.BonusCreditPerson(
    last_name="dupont",
    common_name=None,
    first_names=["alexis"],
    birth_date=datetime.date(1982, 12, 7),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
QF_CUSTODIAN_WITH_CHILDREN = bonus_schemas.BonusCreditPerson(
    last_name="lefebvre",
    common_name=None,
    first_names=["aleixs", "gréôme", "jean-philippe"],
    birth_date=datetime.date(1982, 12, 27),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
DISABILITY_APPLICATION_NOT_FOUND = bonus_schemas.BonusCreditPerson(
    last_name="duboche",
    common_name=None,
    first_names=["jerome"],
    birth_date=datetime.date(2002, 12, 5),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
ADULT_DISABILITY_BENEFICIARY = bonus_schemas.BonusCreditPerson(
    last_name="dupont",
    common_name="martin",
    first_names=["pierre", "richard"],
    birth_date=datetime.date(1987, 12, 1),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
ADULT_DISABILITY_NON_BENEFICIARY = bonus_schemas.BonusCreditPerson(
    last_name="chirac",
    common_name="martin",
    first_names=["jacques"],
    birth_date=datetime.date(1987, 12, 1),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
DISABLED_CHILD_EDUCATION_BENEFICIARY = bonus_schemas.BonusCreditPerson(
    last_name="dupont",
    first_names=["pierre"],
    birth_date=datetime.date(2015, 3, 12),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="75112",
)
DISABLED_CHILD_EDUCATION_RIGHT_OPENING = bonus_schemas.BonusCreditPerson(
    last_name="martin",
    first_names=["sophie", "marie"],
    birth_date=datetime.date(2012, 7, 22),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="69123",
)
DISABLED_CHILD_EDUCATION_NON_BENEFICIARY = bonus_schemas.BonusCreditPerson(
    last_name="bernard",
    first_names=["lucas"],
    birth_date=datetime.date(2010, 1, 5),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="13055",
)
DISABLED_CHILD_DATA_PROVIDER_ERROR = bonus_schemas.BonusCreditPerson(
    last_name="delanque",
    first_names=["jean-marie"],
    birth_date=datetime.date(2008, 6, 15),
    gender=users_models.GenderEnum.M,
    birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)


def get_and_mock_quotient_familial(
    custodian: bonus_schemas.BonusCreditPerson,
    at_date: datetime.date,
    user: users_models.User,
) -> api_particulier.QuotientFamilialResponse:
    """
    Calls the API Particulier Quotient Familial staging endpoint with their staging dataset, to test the HTTP roundtrip.
    Their response is then mocked through previous config fraud check.
    """
    mock_config = _get_last_quotient_familial_config(user)
    if not mock_config:
        return api_particulier.get_quotient_familial(custodian, at_date)

    if not mock_config.http_status_code:
        raise ValueError("Mocked API Response calls must have a defined http_status_code")

    if mock_config.http_status_code == 404:
        mocked_custodian = QF_APPLICATION_NOT_FOUND
    elif mock_config.http_status_code == 422:
        mocked_custodian = PERSON_NOT_FOUND
    elif mock_config.http_status_code == 502:
        mocked_custodian = DATA_PROVIDER_ERROR
    else:
        mocked_custodian = QF_CUSTODIAN_WITH_CHILDREN
    api_particulier_response = api_particulier.get_quotient_familial(mocked_custodian)

    _inject_quotient_familial_mock_config(api_particulier_response, mock_config)

    return api_particulier_response


def _get_last_quotient_familial_config(
    user: users_models.User,
) -> bonus_schemas.QuotientFamilialBonusCreditContent | None:
    config_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        and fraud_check.status == subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]
    if not config_fraud_checks:
        return None

    last_config = config_fraud_checks[-1]  # the user.beneficiaryFraudChecks relationship is ordered

    source_data = last_config.source_data()
    if not isinstance(source_data, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"QuotientFamilialBonusCreditContent was expected while {type(source_data)} was given")

    return source_data


def _inject_quotient_familial_mock_config(
    api_particulier_response: api_particulier.QuotientFamilialResponse,
    mock_config: bonus_schemas.QuotientFamilialBonusCreditContent,
) -> None:
    if mock_config.quotient_familial:
        api_particulier_response.data.quotient_familial = _build_api_quotient_familial_response(
            mock_config.quotient_familial
        )

    if mock_config.children:
        api_particulier_response.data.enfants = [_build_api_person_response(child) for child in mock_config.children]

    if mock_config.householders:
        api_particulier_response.data.allocataires = [
            _build_api_person_response(householder) for householder in mock_config.householders
        ]


def _build_api_quotient_familial_response(
    quotient_familial: bonus_schemas.QuotientFamilialContent,
) -> api_particulier.QuotientFamilial:
    return api_particulier.QuotientFamilial(
        fournisseur=quotient_familial.provider,
        valeur=quotient_familial.value,
        annee=quotient_familial.year,
        mois=quotient_familial.month,
        annee_calcul=quotient_familial.computation_year,
        mois_calcul=quotient_familial.computation_month,
    )


def _build_api_person_response(person: bonus_schemas.BonusCreditPerson) -> api_particulier.ApiParticulierPerson:
    return api_particulier.ApiParticulierPerson(
        nom_naissance=person.last_name,
        nom_usage=person.common_name,
        prenoms=" ".join(person.first_names),
        date_naissance=person.birth_date,
        sexe=person.gender,
    )


def get_and_mock_disabled_adult_allowance(
    person: bonus_schemas.BonusCreditPerson,
    user: users_models.User,
) -> api_particulier.DisabledAdultAllowanceResponse:
    """
    Calls the API Particulier Disabled Adult Allowance staging endpoint with their staging dataset, to test the HTTP roundtrip.
    Their response is then mocked through previous config fraud check.
    """
    mock_config = _get_last_adult_disability_config(user)
    if not mock_config:
        return api_particulier.get_disabled_adult_allowance(person)

    if not mock_config.http_status_code:
        raise ValueError("Mocked API Response calls must have a defined http_status_code")

    if mock_config.http_status_code == 404:
        mocked_person = DISABILITY_APPLICATION_NOT_FOUND
    elif mock_config.http_status_code == 422:
        mocked_person = PERSON_NOT_FOUND
    elif mock_config.http_status_code == 502:
        mocked_person = DATA_PROVIDER_ERROR
    elif not mock_config.is_disability_beneficiary:
        mocked_person = ADULT_DISABILITY_NON_BENEFICIARY
    else:
        mocked_person = ADULT_DISABILITY_BENEFICIARY

    return api_particulier.get_disabled_adult_allowance(mocked_person)


def _get_last_adult_disability_config(
    user: users_models.User,
) -> bonus_schemas.AdultDisabilityBonusCreditContent | None:
    config_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.AAH_BONUS_CREDIT
        and fraud_check.status == subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]
    if not config_fraud_checks:
        return None

    last_config = config_fraud_checks[-1]  # the user.beneficiaryFraudChecks relationship is ordered

    source_data = last_config.source_data()
    if not isinstance(source_data, bonus_schemas.AdultDisabilityBonusCreditContent):
        raise ValueError(f"AdultDisabilityBonusCreditContent was expected while {type(source_data)} was given")

    return source_data


def get_and_mock_disabled_child_education_allowance(
    person: bonus_schemas.BonusCreditPerson,
    user: users_models.User,
) -> api_particulier.DisabledChildEducationAllowanceResponse:
    """
    Calls the API Particulier Disabled Child Education Allowance staging endpoint with their staging dataset, to test the HTTP roundtrip.
    Their response is then mocked through previous config fraud check.
    """
    mock_config = _get_last_disabled_child_education_config(user)
    if not mock_config:
        return api_particulier.get_disabled_child_education_allowance(person)

    if not mock_config.http_status_code:
        raise ValueError("Mocked API Response calls must have a defined http_status_code")

    if mock_config.http_status_code == 404:
        mocked_person = DISABILITY_APPLICATION_NOT_FOUND
    elif mock_config.http_status_code == 422:
        mocked_person = PERSON_NOT_FOUND
    elif mock_config.http_status_code == 502:
        mocked_person = DISABLED_CHILD_DATA_PROVIDER_ERROR
    elif (
        mock_config.disability_beneficiary_status
        == bonus_schemas.DisabledChildEducationBeneficiaryStatus.NON_BENEFICIARY
    ):
        mocked_person = DISABLED_CHILD_EDUCATION_NON_BENEFICIARY
    elif (
        mock_config.disability_beneficiary_status == bonus_schemas.DisabledChildEducationBeneficiaryStatus.RIGHT_OPENING
    ):
        mocked_person = DISABLED_CHILD_EDUCATION_RIGHT_OPENING
    else:
        mocked_person = DISABLED_CHILD_EDUCATION_BENEFICIARY

    return api_particulier.get_disabled_child_education_allowance(mocked_person)


def _get_last_disabled_child_education_config(
    user: users_models.User,
) -> bonus_schemas.DisabledChildEducationBonusCreditContent | None:
    config_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.AEEH_BONUS_CREDIT
        and fraud_check.status == subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]
    if not config_fraud_checks:
        return None

    last_config = config_fraud_checks[-1]  # the user.beneficiaryFraudChecks relationship is ordered

    source_data = last_config.source_data()
    if not isinstance(source_data, bonus_schemas.DisabledChildEducationBonusCreditContent):
        raise ValueError(f"DisabledChildEducationBonusCreditContent was expected while {type(source_data)} was given")

    return source_data
