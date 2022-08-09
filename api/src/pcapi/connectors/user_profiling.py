import datetime
import enum
import logging

import pydantic

from pcapi import settings
import pcapi.core.fraud.models as fraud_models
from pcapi.utils import requests


logger = logging.getLogger(__name__)


SERVICE_TYPE = "all"
EVENT_TYPE = "account_creation"

POLICY = "beneficiary_validation_rules"


class BaseUserProfilingException(Exception):
    pass


class UserProfilingRequestError(BaseUserProfilingException):
    pass


class UserProfilingHTTPError(BaseUserProfilingException):
    pass


class UserProfilingDataResponseError(BaseUserProfilingException):
    pass


class WorkflowType(enum.Enum):
    BENEFICIARY_VALIDATION = "beneficiary_validation"


class LineOfBusiness(enum.Enum):
    B2B = "B2B"
    B2C = "B2C"


class AgentType(enum.Enum):
    BROWSER_COMPUTER = "browser_computer"
    BROWSER_MOBILE = "browser_mobile"
    AGENT_MOBILE = "agent_mobile"


class UserProfilingClient:
    def __init__(self) -> None:
        self.url = settings.USER_PROFILING_URL
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self.base_params = {
            "org_id": settings.USER_PROFILING_ORG_ID,
            "api_key": settings.USER_PROFILING_API_KEY,
        }

    def get_user_profiling_fraud_data(
        self,
        session_id: str,
        user_id: int,
        user_email: str,
        birth_date: datetime.date | None,
        phone_number: str | None,
        workflow_type: WorkflowType,
        ip_address: str,
        line_of_business: LineOfBusiness,
        transaction_id: str,
        agent_type: AgentType,
    ) -> fraud_models.UserProfilingFraudData:
        """Retrieve the user fraud score from UserProfiling database & computation

        session_id: the session id of the profiling done on the phone
        birth_date: the user birth date
        phone_number: the user phone number in international format
        workflow_type: the event type to differeciate a user workflow or a pro workflow
        ip_address: the user IP address
        line_of_business: the user profile : B2B or B2C
        transaction_id: local request identifier
        agent_type: the application origin: must be 'browser_computer', 'browser_mobile', or 'agent_mobile'
        """
        params = {
            # UserProfiling parameters
            "session_id": session_id,
            "service_type": SERVICE_TYPE,
            "event_type": EVENT_TYPE,
            "policy": POLICY,
            "customer_event_type": workflow_type.value,
            # Event metadata
            "input_ip_address": ip_address,
            "line_of_business": line_of_business.value,
            "transaction_id": transaction_id,
            "condition_attrib_5": agent_type.value,
            # Customer data
            "account_login": str(user_id),
            "account_email": user_email,
        }
        if phone_number:
            params["account_telephone"] = phone_number.lstrip("+")
        if birth_date:
            params["account_date_of_birth"] = birth_date.strftime("%Y%m%d")

        params.update(self.base_params)

        try:
            response = self.session.post(self.url, json=params)
        except Exception as exc:
            logger.exception("Network error from UserProfiling (%r)", exc)
            raise UserProfilingHTTPError("Unknown error from UserProfiling)") from exc

        try:
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise UserProfilingHTTPError(f"Error getting response from UserProfiling ({response.status_code})") from exc

        if "error_detail" in data:
            raise UserProfilingRequestError(
                f"Error in parameters sent to UserProfiling: { data['error_detail'] } : {data['request_result']}"
            )

        try:
            return fraud_models.UserProfilingFraudData(**data)
        except pydantic.ValidationError as error:
            logger.warning("Error in UserProfiling response validation", extra={"validation_errors": error.errors()})
            raise UserProfilingDataResponseError("Invalid data received from UserProfiling") from error
