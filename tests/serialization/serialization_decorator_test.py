from typing import Optional
from unittest.mock import patch

from pydantic import BaseModel

from pcapi.flask_app import api
from pcapi.serialization.decorator import spectree_serialize


class TestBodyModel(BaseModel):
    compulsory_int_body: int
    optional_string_body: Optional[str]


class TestQueryModel(BaseModel):
    compulsory_int_query: int
    optinal_string_query: Optional[str]


class TestResponseModel(BaseModel):
    compulsory_int_response: int
    optional_string_response: Optional[str]


class SerializationDecoratorTest:
    def should_return_json_response_with_200(self, app):
        # Given
        @spectree_serialize(response_model=TestResponseModel)
        def mock_func():
            return TestResponseModel(compulsory_int_response=1)

        # When
        response = mock_func()

        # Then
        assert response.status_code == 200
        assert response.json == {
            "compulsory_int_response": 1,
            "optional_string_response": None,
        }

    def should_return_str_response_with_200_when_asked(self, app):
        # Given
        @spectree_serialize(json_format=False)
        def mock_func():
            return "Some response"

        # When
        response = mock_func()

        # Then
        assert response.status_code == 200
        assert response.data.decode("utf8") == "Some response"

    def should_return_json_response_with_custom_status_code(self, app):
        # Given
        @spectree_serialize(response_model=TestResponseModel, on_success_status=217)
        def mock_func():
            return TestResponseModel(compulsory_int_response=1)

        # When
        response = mock_func()

        # Then
        assert response.status_code == 217

    @patch.object(api, "validate")
    def should_call_validation_with_the_right_params(self, mocked_validate):
        # Given
        @spectree_serialize(response_model=TestResponseModel, on_success_status=217)
        def mock_func(body: TestBodyModel, query: TestQueryModel):
            return

        mocked_validate.return_value = TestResponseModel(compulsory_int_response=1)

        body = TestBodyModel(compulsory_int_body=2)
        query = TestQueryModel(compulsory_int_query=3)

        # When
        mock_func(body, query)

        # Then
        assert mocked_validate.called_once()

        _, kwargs = mocked_validate.call_args
        assert kwargs["json"] == TestBodyModel
        assert kwargs["query"] == TestQueryModel
        assert kwargs["resp"].code_models["HTTP_217"] == TestResponseModel
