"""Tests for PokeTodo Pydantic serialization schemas."""

from pcapi.routes.serialization.poke_todo_serialize import CreatePokeTodoBodyModel
from pcapi.routes.serialization.poke_todo_serialize import UpdatePokeTodoBodyModel


class CreatePokeTodoBodyModelSchemaTest:
    def test_title_has_error_messages_extension(self):
        schema = CreatePokeTodoBodyModel.model_json_schema()
        title_schema = schema["properties"]["title"]

        assert "x-error-messages" in title_schema
        assert title_schema["x-error-messages"] == {
            "max_length": "Title cannot exceed 255 characters",
        }

    def test_title_has_max_length(self):
        schema = CreatePokeTodoBodyModel.model_json_schema()
        title_schema = schema["properties"]["title"]

        assert title_schema["maxLength"] == 255


class UpdatePokeTodoBodyModelSchemaTest:
    def test_title_has_error_messages_extension(self):
        schema = UpdatePokeTodoBodyModel.model_json_schema()
        title_property = schema["properties"]["title"]

        assert "x-error-messages" in title_property
        assert title_property["x-error-messages"] == {
            "max_length": "Title cannot exceed 255 characters",
        }

    def test_title_string_variant_has_error_messages_extension(self):
        schema = UpdatePokeTodoBodyModel.model_json_schema()
        title_property = schema["properties"]["title"]
        string_variant = next(v for v in title_property["anyOf"] if v.get("type") == "string")

        assert "x-error-messages" in string_variant
        assert string_variant["x-error-messages"] == {
            "max_length": "Title cannot exceed 255 characters",
        }

    def test_title_has_max_length(self):
        schema = UpdatePokeTodoBodyModel.model_json_schema()
        title_property = schema["properties"]["title"]
        string_variant = next(v for v in title_property["anyOf"] if v.get("type") == "string")

        assert string_variant["maxLength"] == 255
