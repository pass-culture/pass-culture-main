"""Tests for PokeTodo CRUD routes."""

import pytest

from pcapi.core.poke_todo.models import PokeTodo
from pcapi.core.poke_todo.models import PokeTodoPriority
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class ListPokeTodosTest:
    def test_returns_empty_list(self, client):
        response = client.get("/poke-todos")

        assert response.status_code == 200
        assert response.json == []

    def test_returns_all_todos(self, client):
        todo_one = PokeTodo(title="First todo")
        todo_two = PokeTodo(title="Second todo", description="Some description")
        db.session.add_all([todo_one, todo_two])
        db.session.flush()

        response = client.get("/poke-todos")

        assert response.status_code == 200
        assert len(response.json) == 2
        titles = {item["title"] for item in response.json}
        assert titles == {"First todo", "Second todo"}


@pytest.mark.usefixtures("db_session")
class GetPokeTodoTest:
    def test_returns_todo(self, client):
        todo = PokeTodo(title="My todo", description="My description")
        db.session.add(todo)
        db.session.flush()

        response = client.get(f"/poke-todos/{todo.id}")

        assert response.status_code == 200
        assert response.json["title"] == "My todo"
        assert response.json["description"] == "My description"
        assert response.json["isCompleted"] is False
        assert response.json["priority"] == "low"
        assert response.json["dueDate"] is None
        assert "dateCreated" in response.json

    def test_returns_404_for_unknown_id(self, client):
        response = client.get("/poke-todos/99999")

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class CreatePokeTodoTest:
    def test_creates_todo_with_title_only(self, client):
        response = client.post("/poke-todos", json={"title": "New todo"})

        assert response.status_code == 201
        assert response.json["title"] == "New todo"
        assert response.json["description"] is None
        assert response.json["isCompleted"] is False
        assert response.json["priority"] == "low"
        assert response.json["dueDate"] is None

        todo = db.session.query(PokeTodo).one()
        assert todo.title == "New todo"

    def test_creates_todo_with_description(self, client):
        response = client.post("/poke-todos", json={"title": "New todo", "description": "Some details"})

        assert response.status_code == 201
        assert response.json["description"] == "Some details"

    def test_creates_todo_with_priority_and_due_date(self, client):
        response = client.post(
            "/poke-todos",
            json={
                "title": "Urgent task",
                "priority": "high",
                "dueDate": "2026-12-31T23:59:00",
            },
        )

        assert response.status_code == 201
        assert response.json["priority"] == "high"
        assert response.json["dueDate"] is not None

        todo = db.session.query(PokeTodo).one()
        assert todo.priority == PokeTodoPriority.HIGH

    def test_creates_todo_with_medium_priority_and_due_date(self, client):
        response = client.post(
            "/poke-todos",
            json={
                "title": "Normal task",
                "priority": "medium",
                "dueDate": "2026-06-15T12:00:00",
            },
        )

        assert response.status_code == 201
        assert response.json["priority"] == "medium"

    def test_returns_400_when_title_missing(self, client):
        response = client.post("/poke-todos", json={})

        assert response.status_code == 400

    def test_returns_400_when_title_too_long(self, client):
        response = client.post("/poke-todos", json={"title": "x" * 256})

        assert response.status_code == 400

    def test_returns_400_when_high_priority_without_due_date(self, client):
        response = client.post(
            "/poke-todos",
            json={"title": "Urgent task", "priority": "high"},
        )

        assert response.status_code == 400

    def test_returns_400_when_low_priority_with_due_date(self, client):
        response = client.post(
            "/poke-todos",
            json={
                "title": "Chill task",
                "priority": "low",
                "dueDate": "2026-12-31T23:59:00",
            },
        )

        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class UpdatePokeTodoTest:
    def test_updates_title(self, client):
        todo = PokeTodo(title="Old title")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(f"/poke-todos/{todo.id}", json={"title": "New title"})

        assert response.status_code == 200
        assert response.json["title"] == "New title"

    def test_updates_is_completed(self, client):
        todo = PokeTodo(title="My todo", description="Has a description")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(
            f"/poke-todos/{todo.id}",
            json={"isCompleted": True, "description": "Has a description"},
        )

        assert response.status_code == 200
        assert response.json["isCompleted"] is True

    def test_updates_description(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(f"/poke-todos/{todo.id}", json={"description": "Updated"})

        assert response.status_code == 200
        assert response.json["description"] == "Updated"

    def test_updates_priority(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(f"/poke-todos/{todo.id}", json={"priority": "medium"})

        assert response.status_code == 200
        assert response.json["priority"] == "medium"

    def test_updates_priority_to_high_with_due_date(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(
            f"/poke-todos/{todo.id}",
            json={"priority": "high", "dueDate": "2026-12-31T23:59:00"},
        )

        assert response.status_code == 200
        assert response.json["priority"] == "high"
        assert response.json["dueDate"] is not None

    def test_sets_date_updated(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(f"/poke-todos/{todo.id}", json={"title": "Changed"})

        assert response.status_code == 200
        assert response.json["dateUpdated"] is not None

    def test_returns_404_for_unknown_id(self, client):
        response = client.patch("/poke-todos/99999", json={"title": "Nope"})

        assert response.status_code == 404

    def test_returns_400_when_completing_without_description(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(
            f"/poke-todos/{todo.id}",
            json={"isCompleted": True},
        )

        assert response.status_code == 400

    def test_returns_400_when_setting_high_priority_without_due_date(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(
            f"/poke-todos/{todo.id}",
            json={"priority": "high"},
        )

        assert response.status_code == 400

    def test_returns_400_when_setting_low_priority_with_due_date(self, client):
        todo = PokeTodo(title="My todo")
        db.session.add(todo)
        db.session.flush()

        response = client.patch(
            f"/poke-todos/{todo.id}",
            json={"priority": "low", "dueDate": "2026-12-31T23:59:00"},
        )

        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class DeletePokeTodoTest:
    def test_deletes_todo(self, client):
        todo = PokeTodo(title="To delete")
        db.session.add(todo)
        db.session.flush()
        todo_id = todo.id

        response = client.delete(f"/poke-todos/{todo_id}")

        assert response.status_code == 204
        assert db.session.query(PokeTodo).filter_by(id=todo_id).one_or_none() is None

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete("/poke-todos/99999")

        assert response.status_code == 404
