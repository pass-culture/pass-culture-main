"""Pydantic v2 serialization schemas for PokeTodo CRUD operations."""

import datetime
import typing

from pydantic import Field
from pydantic import RootModel
from pydantic import model_validator

from pcapi.core.poke_todo.models import PokeTodoPriority
from pcapi.routes.serialization import HttpBodyModel


class PokeTodoResponseModel(HttpBodyModel):
    id: int
    title: str
    description: str | None
    priority: PokeTodoPriority
    due_date: datetime.datetime | None
    is_completed: bool
    date_created: datetime.datetime
    date_updated: datetime.datetime | None


class PokeTodoListResponseModel(RootModel):
    root: list[PokeTodoResponseModel]


def _add_create_cross_field_rules(schema: dict[str, typing.Any]) -> None:
    """Inject cross-field validation rules as OpenAPI extensions."""
    schema["x-validation-rules"] = [
        {
            "rule": "conditional-required",
            "when": {"field": "priority", "equals": "high"},
            "then": {"field": "dueDate", "required": True},
            "message": "Due date is required for high-priority todos",
        },
        {
            "rule": "mutual-dependency",
            "when": {"field": "dueDate", "present": True},
            "then": {"field": "priority", "not_equals": "low"},
            "message": "Low-priority todos cannot have a due date",
        },
    ]


class CreatePokeTodoBodyModel(HttpBodyModel):
    model_config = HttpBodyModel.model_config.copy()
    model_config["json_schema_extra"] = _add_create_cross_field_rules

    title: str = Field(
        max_length=255,
        json_schema_extra={
            "x-error-messages": {
                "max_length": "Title cannot exceed 255 characters",
            }
        },
    )
    description: str | None = None
    priority: PokeTodoPriority = PokeTodoPriority.LOW
    due_date: datetime.datetime | None = None

    @model_validator(mode="after")
    def validate_cross_field_rules(self) -> typing.Self:
        errors: list[str] = []

        if self.priority == PokeTodoPriority.HIGH and self.due_date is None:
            errors.append("Due date is required for high-priority todos")

        if self.due_date is not None and self.priority == PokeTodoPriority.LOW:
            errors.append("Low-priority todos cannot have a due date")

        if errors:
            raise ValueError("; ".join(errors))

        return self


def _propagate_error_messages_into_any_of(schema: dict[str, typing.Any]) -> None:
    """Push x-error-messages from property level into anyOf string variants.

    Pydantic places json_schema_extra at the property level for optional fields,
    but OpenAPI consumers need it on the string variant inside anyOf.
    """
    properties = schema.get("properties", {})
    for property_schema in properties.values():
        error_messages = property_schema.get("x-error-messages")
        if error_messages is None:
            continue
        any_of = property_schema.get("anyOf")
        if any_of is None:
            continue
        for variant in any_of:
            if variant.get("type") == "string":
                variant["x-error-messages"] = error_messages


def _add_update_cross_field_rules(schema: dict[str, typing.Any]) -> None:
    """Inject cross-field validation rules as OpenAPI extensions."""
    _propagate_error_messages_into_any_of(schema)
    schema["x-validation-rules"] = [
        {
            "rule": "conditional-required",
            "when": {"field": "isCompleted", "equals": True},
            "then": {"field": "description", "required": True},
            "message": "Description is required when completing a todo",
        },
        {
            "rule": "conditional-required",
            "when": {"field": "priority", "equals": "high"},
            "then": {"field": "dueDate", "required": True},
            "message": "Due date is required for high-priority todos",
        },
        {
            "rule": "mutual-dependency",
            "when": {"field": "dueDate", "present": True},
            "then": {"field": "priority", "not_equals": "low"},
            "message": "Low-priority todos cannot have a due date",
        },
    ]


class UpdatePokeTodoBodyModel(HttpBodyModel):
    model_config = HttpBodyModel.model_config.copy()
    model_config["json_schema_extra"] = _add_update_cross_field_rules

    title: str | None = Field(
        default=None,
        max_length=255,
        json_schema_extra={
            "x-error-messages": {
                "max_length": "Title cannot exceed 255 characters",
            }
        },
    )
    description: str | None = None
    priority: PokeTodoPriority | None = None
    due_date: datetime.datetime | None = None
    is_completed: bool | None = None

    @model_validator(mode="after")
    def validate_cross_field_rules(self) -> typing.Self:
        errors: list[str] = []

        if self.is_completed is True and not self.description:
            errors.append("Description is required when completing a todo")

        if self.priority == PokeTodoPriority.HIGH and self.due_date is None:
            errors.append("Due date is required for high-priority todos")

        if self.due_date is not None and self.priority == PokeTodoPriority.LOW:
            errors.append("Low-priority todos cannot have a due date")

        if errors:
            raise ValueError("; ".join(errors))

        return self
