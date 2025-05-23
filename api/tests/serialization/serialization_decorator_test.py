from unittest.mock import Mock
from unittest.mock import patch

from flask.blueprints import Blueprint
from werkzeug.datastructures import MultiDict

from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import _transform_query_args_to_dict
from pcapi.serialization.decorator import feature_flag_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse


class TestBodyModel(BaseModel):
    compulsory_int_body: int
    optional_string_body: str | None


class TestQueryModel(BaseModel):
    compulsory_int_query: int
    optinal_string_query: str | None


class TestResponseModel(BaseModel):
    compulsory_int_response: int
    optional_string_response: str | None


endpoint_method = Mock()
test_blueprint = Blueprint("test_blueprint", __name__)
test_bookings_blueprint = Blueprint("test_bookings_blueprint", __name__)


@test_blueprint.route("/test", methods=["GET"])
@spectree_serialize(on_success_status=204)
def spectree_get_test_endpoint():
    endpoint_method()


@test_blueprint.route("/test", methods=["POST"])
@spectree_serialize(on_success_status=204)
def spectree_post_test_endpoint():
    endpoint_method()


@test_blueprint.route("/test-with-pydantic-model-for-body", methods=["GET"])
@spectree_serialize(on_success_status=204)
def spectree_get_test_with_pydantic_model_endpoint(body: TestBodyModel):
    endpoint_method()


@test_blueprint.route("/test-with-pydantic-model-for-body", methods=["POST"])
@spectree_serialize(on_success_status=204)
def spectree_post_test_with_pydantic_model_endpoint(body: TestBodyModel):
    endpoint_method()


_active_ff_mock = Mock()
_active_ff_mock.is_active.return_value = True

_inactive_ff_mock = Mock()
_inactive_ff_mock.is_active.return_value = False


@test_blueprint.route("/test-ff-active", methods=["GET"])
@feature_flag_required(feature_flag=_active_ff_mock)
def spectree_get_test_ff_active_endpoint():
    return {}


@test_blueprint.route("/test-ff-inactive", methods=["GET"])
@feature_flag_required(feature_flag=_inactive_ff_mock)
def spectree_get_test_ff_inactive_endpoint():
    return {}


@test_blueprint.route("/body-validation-with-http-responses", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_BOOKING_CANCELLATION_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_403_COLLECTIVE_OFFER_INACTIVE_INSTITUTION
            | http_responses.HTTP_404_SOME_RESOURCE_NOT_FOUND
        )
    ),
)
def spectree_body_validation_2(body: TestQueryModel):
    return


@test_blueprint.route("/body-validation", methods=["POST"])
@spectree_serialize(on_success_status=206)
def spectree_body_validation(body: TestQueryModel):
    return


@test_blueprint.route("/form-validation", methods=["POST"])
@spectree_serialize(on_success_status=206)
def spectree_form_validation(form: TestQueryModel):
    return


@test_bookings_blueprint.route("/bookings", methods=["GET"])
@spectree_serialize(on_success_status=204)
def spectree_get_booking_test_endpoint():
    endpoint_method()


@test_bookings_blueprint.route("/bookings", methods=["POST"])
@spectree_serialize(on_success_status=204)
def spectree_post_booking_test_endpoint():
    endpoint_method()


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
        @spectree_serialize(response_model=TestResponseModel, on_success_status=206)
        def mock_func():
            return TestResponseModel(compulsory_int_response=1)

        # When
        response = mock_func()

        # Then
        assert response.status_code == 206

    @patch("pcapi.routes.apis.api.validate")
    def should_call_validation_with_the_right_params(self, mocked_validate):
        # Given
        @spectree_serialize(response_model=TestResponseModel, on_success_status=206)
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
        assert kwargs["resp"].code_models["HTTP_206"] == TestResponseModel

    def test_get_with_content_type_but_without_body(self, client):
        response = client.get("/v2/bookings", headers={"Content-Type": "application/json"})
        assert response.status_code == 204

    def test_post_with_content_type_with_invalid_body(self, client, caplog):
        response = client.post(
            "/v2/bookings",
            headers={"Content-Type": "application/json"},
            raw_json='{"test": "otherTest" "wrongJSON": "why?"}',
        )
        assert response.status_code == 204

    def test_get_with_content_type_but_without_body_throws_error(self, client):
        response = client.get(
            "/test-blueprint/test-with-pydantic-model-for-body", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400

    def test_post_with_content_type_with_invalid_body_throw_error(self, client, caplog):
        response = client.post(
            "/test-blueprint/test-with-pydantic-model-for-body",
            headers={"Content-Type": "application/json"},
            raw_json='{"test": "otherTest" "wrongJSON": "why?"}',
        )
        assert response.status_code == 400

    def test_http_form_validation(self, client):
        response = client.post(
            "/test-blueprint/form-validation", form=None, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 400
        assert response.json == {
            "compulsory_int_query": ["Ce champ est obligatoire"],
        }

    def test_post_without_content_type_throws_400(self, client):
        response = client.post("/test-blueprint/body-validation", headers={})
        assert response.status_code == 400
        assert response.get_data() == b'Please send a "Content-Type: application/json" HTTP header'

    def test_post_without_content_with_incorrect_content_type_throws_400(self, client):
        response = client.post(
            "/test-blueprint/body-validation-with-http-responses",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            json={},
        )
        assert response.status_code == 400
        assert response.get_data() == b'Please send a "Content-Type: application/json" HTTP header'


class LinkRouteToFeatureFlagDecoratorTest:
    def test_should_return_200(self, client):
        response = client.get("/test-blueprint/test-ff-active")
        assert response.status_code == 200

    def test_should_return_404(self, client):
        response = client.get("/test-blueprint/test-ff-inactive")
        assert response.status_code == 404


class TransformQueryArgsToDictTest:
    def test_basic_transformation(self, client):
        query_params = MultiDict([("a", "1"), ("b", "2"), ("c", "3")])
        use_as_list = ["b"]
        expected = {"a": "1", "b": ["2"], "c": "3"}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected

    def test_multiple_values_for_list_param(self, client):
        query_params = MultiDict([("a", "1"), ("b", "2"), ("b", "3"), ("c", "4")])
        use_as_list = ["b"]
        expected = {"a": "1", "b": ["2", "3"], "c": "4"}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected

    def test_empty_query_params(self, client):
        query_params = MultiDict()
        use_as_list = ["a"]
        expected = {}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected

    def test_all_params_as_list(self, client):
        query_params = MultiDict([("a", "1"), ("b", "2"), ("c", "3")])
        use_as_list = ["a", "b", "c"]
        expected = {"a": ["1"], "b": ["2"], "c": ["3"]}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected

    def test_no_params_as_list(self, client):
        query_params = MultiDict([("a", "1"), ("b", "2"), ("c", "3")])
        use_as_list = []
        expected = {"a": "1", "b": "2", "c": "3"}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected

    def test_empty_string_as_list_param(self, client):
        query_params = MultiDict([("a", "1"), ("b", ""), ("c", "3")])
        use_as_list = ["b"]
        expected = {"a": "1", "b": [""], "c": "3"}
        assert _transform_query_args_to_dict(query_params, use_as_list) == expected
