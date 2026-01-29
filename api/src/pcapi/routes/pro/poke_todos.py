"""Flask CRUD routes for the PokeTodo experimental entity."""

import datetime

from pcapi.core.poke_todo.models import PokeTodo
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import poke_todo_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@public_api.route("/poke-todos", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=poke_todo_serialize.PokeTodoListResponseModel,
    api=blueprint.pro_private_schema,
)
def list_poke_todos() -> poke_todo_serialize.PokeTodoListResponseModel:
    todos = db.session.query(PokeTodo).order_by(PokeTodo.date_created.desc()).all()
    return poke_todo_serialize.PokeTodoListResponseModel(
        [poke_todo_serialize.PokeTodoResponseModel.model_validate(todo) for todo in todos]
    )


@public_api.route("/poke-todos/<int:todo_id>", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=poke_todo_serialize.PokeTodoResponseModel,
    api=blueprint.pro_private_schema,
)
def get_poke_todo(todo_id: int) -> poke_todo_serialize.PokeTodoResponseModel:
    todo = db.session.query(PokeTodo).filter_by(id=todo_id).one_or_none()
    if not todo:
        raise ResourceNotFoundError()
    return poke_todo_serialize.PokeTodoResponseModel.model_validate(todo)


@public_api.route("/poke-todos", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=poke_todo_serialize.PokeTodoResponseModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def create_poke_todo(body: poke_todo_serialize.CreatePokeTodoBodyModel) -> poke_todo_serialize.PokeTodoResponseModel:
    todo = PokeTodo(
        title=body.title,
        description=body.description,
        priority=body.priority,
        due_date=body.due_date,
    )
    db.session.add(todo)
    db.session.flush()
    return poke_todo_serialize.PokeTodoResponseModel.model_validate(todo)


@public_api.route("/poke-todos/<int:todo_id>", methods=["PATCH"])
@atomic()
@spectree_serialize(
    response_model=poke_todo_serialize.PokeTodoResponseModel,
    api=blueprint.pro_private_schema,
)
def update_poke_todo(
    todo_id: int, body: poke_todo_serialize.UpdatePokeTodoBodyModel
) -> poke_todo_serialize.PokeTodoResponseModel:
    todo = db.session.query(PokeTodo).filter_by(id=todo_id).one_or_none()
    if not todo:
        raise ResourceNotFoundError()

    if body.title is not None:
        todo.title = body.title
    if body.description is not None:
        todo.description = body.description
    if body.priority is not None:
        todo.priority = body.priority
    if body.due_date is not None:
        todo.due_date = body.due_date
    if body.is_completed is not None:
        todo.is_completed = body.is_completed

    todo.date_updated = datetime.datetime.utcnow()
    db.session.flush()
    return poke_todo_serialize.PokeTodoResponseModel.model_validate(todo)


@public_api.route("/poke-todos/<int:todo_id>", methods=["DELETE"])
@atomic()
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_poke_todo(todo_id: int) -> None:
    todo = db.session.query(PokeTodo).filter_by(id=todo_id).one_or_none()
    if not todo:
        raise ResourceNotFoundError()
    db.session.delete(todo)
    db.session.flush()
