import datetime

import pytest

from pcapi import settings
from pcapi.connectors import user_profiling
import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_settings

from . import user_profiling_fixtures


USER_PROFILING_URL = "https://example.com/path"


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_error(requests_mock):
    requests_mock.register_uri("POST", settings.USER_PROFILING_URL, json={}, status_code=500)

    handler = user_profiling.UserProfilingClient()
    with pytest.raises(user_profiling.UserProfilingHTTPError):
        handler.get_user_profiling_fraud_data(
            session_id="fake-session-id",
            user_id="fake-user-id",
            user_email="firstname.lastname@example.com",
            birth_date=datetime.date(1999, 6, 5),
            phone_number="+33712345678",
            workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
            ip_address="127.0.0.1",
            line_of_business=user_profiling.LineOfBusiness.B2B,
            transaction_id="random-transaction-id",
            agent_type=user_profiling.AgentType.AGENT_MOBILE,
        )


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_fails(requests_mock):
    requests_mock.register_uri(
        "POST", settings.USER_PROFILING_URL, json=user_profiling_fixtures.PARAMETER_ERROR_RESPONSE, status_code=200
    )

    handler = user_profiling.UserProfilingClient()
    with pytest.raises(user_profiling.UserProfilingRequestError):
        handler.get_user_profiling_fraud_data(
            session_id="fake-session-id",
            user_id="fake-user-id",
            user_email="firstname.lastname@example.com",
            birth_date=datetime.date(1999, 6, 5),
            phone_number="+33712345678",
            workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
            ip_address="127.0.0.1",
            line_of_business=user_profiling.LineOfBusiness.B2B,
            transaction_id="random-transaction-id",
            agent_type=user_profiling.AgentType.AGENT_MOBILE,
        )


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data(requests_mock):
    matcher = requests_mock.register_uri(
        "POST", settings.USER_PROFILING_URL, json=user_profiling_fixtures.CORRECT_RESPONSE, status_code=200
    )

    handler = user_profiling.UserProfilingClient()
    profiling_data = handler.get_user_profiling_fraud_data(
        session_id="fake-session-id",
        user_id="fake-user-id",
        user_email="firstname.lastname@example.com",
        birth_date=datetime.date(1999, 6, 5),
        phone_number="+33712345678",
        workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
        ip_address="127.0.0.1",
        line_of_business=user_profiling.LineOfBusiness.B2B,
        transaction_id="random-transaction-id",
        agent_type=user_profiling.AgentType.AGENT_MOBILE,
    )

    assert isinstance(profiling_data, fraud_models.UserProfilingFraudData)
    assert profiling_data.account_email_result == user_profiling_fixtures.CORRECT_RESPONSE["account_email_result"]
    assert profiling_data.account_email_score == int(user_profiling_fixtures.CORRECT_RESPONSE["account_email_score"])
    assert (
        profiling_data.account_telephone_result == user_profiling_fixtures.CORRECT_RESPONSE["account_telephone_result"]
    )
    assert profiling_data.account_telephone_score == int(
        user_profiling_fixtures.CORRECT_RESPONSE["account_telephone_score"]
    )
    assert profiling_data.bb_bot_rating == user_profiling_fixtures.CORRECT_RESPONSE["bb_bot_rating"]
    assert profiling_data.bb_bot_score == float(user_profiling_fixtures.CORRECT_RESPONSE["bb_bot_score"])
    assert profiling_data.bb_fraud_rating == user_profiling_fixtures.CORRECT_RESPONSE["bb_fraud_rating"]
    assert profiling_data.bb_fraud_score == float(user_profiling_fixtures.CORRECT_RESPONSE["bb_fraud_score"])
    assert profiling_data.device_id == user_profiling_fixtures.CORRECT_RESPONSE["device_id"]
    assert profiling_data.digital_id_result == user_profiling_fixtures.CORRECT_RESPONSE["digital_id_result"]
    assert profiling_data.digital_id_trust_score == float(
        user_profiling_fixtures.CORRECT_RESPONSE["digital_id_trust_score"]
    )
    assert (
        profiling_data.digital_id_trust_score_rating
        == user_profiling_fixtures.CORRECT_RESPONSE["digital_id_trust_score_rating"]
    )
    assert profiling_data.digital_id_confidence == int(
        user_profiling_fixtures.CORRECT_RESPONSE["digital_id_confidence"]
    )
    assert (
        profiling_data.digital_id_confidence_rating
        == user_profiling_fixtures.CORRECT_RESPONSE["digital_id_confidence_rating"]
    )

    assert matcher.call_count == 1

    request_body = matcher.last_request.json()
    assert request_body["session_id"] == "fake-session-id"
    assert request_body["account_email"] == "firstname.lastname@example.com"
    assert request_body["customer_event_type"] == user_profiling.WorkflowType.BENEFICIARY_VALIDATION.value
    assert request_body["line_of_business"] == user_profiling.LineOfBusiness.B2B.value
    assert request_body["condition_attrib_5"] == user_profiling.AgentType.AGENT_MOBILE.value


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_without_correct_session_id(requests_mock):
    request = user_profiling_fixtures.CORRECT_RESPONSE.copy()
    request["unknown_session"] = "yes"
    requests_mock.register_uri("POST", settings.USER_PROFILING_URL, json=request, status_code=200)

    handler = user_profiling.UserProfilingClient()
    profiling_data = handler.get_user_profiling_fraud_data(
        session_id="fake-session-id",
        user_id="fake-user-id",
        user_email="firstname.lastname@example.com",
        birth_date=datetime.date(1999, 6, 5),
        phone_number="+33712345678",
        workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
        ip_address="127.0.0.1",
        line_of_business=user_profiling.LineOfBusiness.B2B,
        transaction_id="random-transaction-id",
        agent_type=user_profiling.AgentType.AGENT_MOBILE,
    )

    assert isinstance(profiling_data, fraud_models.UserProfilingFraudData)
    assert profiling_data.unknown_session == "yes"


@pytest.mark.parametrize("empty_field", ["account_email_score", "account_telephone_score"])
@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_empty_fields(requests_mock, empty_field):

    user_profiling_response = user_profiling_fixtures.CORRECT_RESPONSE.copy()
    del user_profiling_response[empty_field]
    requests_mock.register_uri("POST", settings.USER_PROFILING_URL, json=user_profiling_response, status_code=200)

    handler = user_profiling.UserProfilingClient()
    profiling_data = handler.get_user_profiling_fraud_data(
        session_id="fake-session-id",
        user_id="fake-user-id",
        user_email="firstname.lastname@example.com",
        birth_date=datetime.date(1999, 6, 5),
        phone_number="+33712345678",
        workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
        ip_address="127.0.0.1",
        line_of_business=user_profiling.LineOfBusiness.B2B,
        transaction_id="random-transaction-id",
        agent_type=user_profiling.AgentType.AGENT_MOBILE,
    )

    assert isinstance(profiling_data, fraud_models.UserProfilingFraudData)


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_format_phone(requests_mock):
    matcher = requests_mock.register_uri(
        "POST", settings.USER_PROFILING_URL, json=user_profiling_fixtures.CORRECT_RESPONSE, status_code=200
    )

    handler = user_profiling.UserProfilingClient()
    handler.get_user_profiling_fraud_data(
        session_id="fake-session-id",
        user_id="fake-user-id",
        user_email="firstname.lastname@example.com",
        birth_date=datetime.date(1999, 6, 5),
        phone_number="+33712345678",
        workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
        ip_address="127.0.0.1",
        line_of_business=user_profiling.LineOfBusiness.B2B,
        transaction_id="random-transaction-id",
        agent_type=user_profiling.AgentType.AGENT_MOBILE,
    )

    assert matcher.last_request.json()["account_telephone"] == "33712345678"


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_date_of_birth_empty(requests_mock):
    matcher = requests_mock.register_uri(
        "POST", settings.USER_PROFILING_URL, json=user_profiling_fixtures.CORRECT_RESPONSE, status_code=200
    )

    handler = user_profiling.UserProfilingClient()
    handler.get_user_profiling_fraud_data(
        session_id="fake-session-id",
        user_id="fake-user-id",
        user_email="firstname.lastname@example.com",
        birth_date=None,
        phone_number="+33712345678",
        workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
        ip_address="127.0.0.1",
        line_of_business=user_profiling.LineOfBusiness.B2B,
        transaction_id="random-transaction-id",
        agent_type=user_profiling.AgentType.AGENT_MOBILE,
    )

    assert "account_date_of_birth" not in matcher.last_request.json().keys()


@override_settings(
    USER_PROFILING_ORG_ID="fake-orgid", USER_PROFILING_API_KEY="fake_api_key", USER_PROFILING_URL=USER_PROFILING_URL
)
def test_get_profiling_data_incorrect_return(requests_mock):
    requests_mock.register_uri(
        "POST", settings.USER_PROFILING_URL, json=user_profiling_fixtures.INVALID_PROFILING_RESPONSE, status_code=200
    )

    handler = user_profiling.UserProfilingClient()
    with pytest.raises(user_profiling.UserProfilingDataResponseError):
        handler.get_user_profiling_fraud_data(
            session_id="fake-session-id",
            user_id="fake-user-id",
            user_email="firstname.lastname@example.com",
            birth_date=None,
            phone_number="+33712345678",
            workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
            ip_address="127.0.0.1",
            line_of_business=user_profiling.LineOfBusiness.B2B,
            transaction_id="random-transaction-id",
            agent_type=user_profiling.AgentType.AGENT_MOBILE,
        )
