"""
Wrapper around the API Particulier connector that allows configuration of their
reponse through config BeneficiaryFraudChecks.

The API Particulier staging dataset is documented at
https://github.com/etalab/siade_staging_data/tree/develop/payloads/api_particulier_v3_cnav_quotient_familial_with_civility
"""

import datetime

from pcapi.connectors import api_particulier
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models


NOT_FOUND_CUSTODIAN = bonus_schemas.QuotientFamilialCustodian(
    last_name="dupont",
    common_name=None,
    first_names=["alexis"],
    birth_date=datetime.date(1982, 12, 7),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code=api_particulier.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)
CUSTODIAN_WITH_CHILDREN = bonus_schemas.QuotientFamilialCustodian(
    last_name="lefebvre",
    common_name=None,
    first_names=["aleixs", "gréôme", "jean-philippe"],
    birth_date=datetime.date(1982, 12, 27),
    gender=users_models.GenderEnum.F,
    birth_country_cog_code=api_particulier.FRANCE_INSEE_CODE,
    birth_city_cog_code="08480",
)


def get_and_mock_quotient_familial(
    custodian: bonus_schemas.QuotientFamilialCustodian,
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
        mocked_custodian = NOT_FOUND_CUSTODIAN
    else:
        mocked_custodian = CUSTODIAN_WITH_CHILDREN
    api_particulier_response = api_particulier.get_quotient_familial(mocked_custodian)

    _inject_mock_config(api_particulier_response, mock_config)

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


def _inject_mock_config(
    api_particulier_response: api_particulier.QuotientFamilialResponse,
    mock_config: bonus_schemas.QuotientFamilialBonusCreditContent,
) -> None:
    if mock_config.quotient_familial:
        api_particulier_response.data.quotient_familial = _build_api_quotient_familial_response(
            mock_config.quotient_familial
        )

    if mock_config.children:
        api_particulier_response.data.enfants = [_build_api_enfants_response(child) for child in mock_config.children]
    else:
        api_particulier_response.data.enfants = []


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


def _build_api_enfants_response(child: bonus_schemas.QuotientFamilialChild) -> api_particulier.QuotientFamilialPerson:
    return api_particulier.QuotientFamilialPerson(
        nom_naissance=child.last_name,
        nom_usage=child.common_name,
        prenoms=" ".join(child.first_names),
        date_naissance=child.birth_date,
        sexe=child.gender,
    )
