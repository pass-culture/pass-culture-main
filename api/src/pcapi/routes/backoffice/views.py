from typing import Any

from flask import render_template
from flask.views import View
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.models import Model
from pcapi.models import db


class DetailView(View):
    model: Any
    template: str

    def init_response(self) -> Any:
        pass

    def item_exists(self, item_id: int) -> bool:
        return db.session.execute(db.session.query(sa.exists().where(self.model.id == item_id))).scalar()

    def _get_item(self, item_id: int):
        return db.session.get(self.model, {"id": item_id})

    def get_item_or_404(self, item_id: int) -> Model:
        self.init_response()
        item = self._get_item(item_id)
        if not item:
            raise NotFound()
        return item

    def dispatch_request(self, item_id: int) -> Any:
        self.item = self.get_item_or_404(item_id)
        return render_template(self.template, **self.get_context())

    def get_context(self) -> dict:
        return {
            "item": self.item,
        }
