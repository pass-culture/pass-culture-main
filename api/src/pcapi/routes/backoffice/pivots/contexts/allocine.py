import typing

from flask_login import current_user
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents

from .. import forms
from .base import PivotContext


class AllocineContext(PivotContext):
    @classmethod
    def pivot_name(cls) -> str:
        return "AlloCine"

    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.AllocinePivot

    @classmethod
    def list_pivots(cls, query_string: str | None = None) -> list[providers_models.AllocinePivot]:
        query = providers_models.AllocinePivot.query.options(
            sa.orm.joinedload(providers_models.AllocinePivot.venue).load_only(
                offerers_models.Venue.name,
            )
        )
        if query_string:
            if query_string.isnumeric():
                query = query.filter(providers_models.AllocinePivot.venueId == int(query_string))
            else:
                query = query.join(providers_models.AllocinePivot.venue).filter(
                    sa.or_(
                        sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(
                            f"%{clean_accents(query_string)}%"
                        ),
                        providers_models.AllocinePivot.theaterId == query_string,
                    )
                )
        return query.all()

    @classmethod
    def get_form(cls) -> forms.EditAllocineForm:
        return forms.EditAllocineForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditAllocineForm:
        pivot = providers_models.AllocinePivot.query.filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()
        return forms.EditAllocineForm(
            venue_id=[pivot.venueId],
            theater_id=pivot.theaterId,
            internal_id=pivot.internalId,
        )

    @classmethod
    def create_pivot(cls, form: forms.EditAllocineForm) -> bool:
        pivot = providers_models.AllocinePivot(
            venueId=form.venue_id.data[0],
            theaterId=form.theater_id.data,
            internalId=form.internal_id.data,
        )
        db.session.add(pivot)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditAllocineForm, pivot_id: int) -> bool:
        pivot = providers_models.AllocinePivot.query.filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()
        pivot.venueId = form.venue_id.data[0]
        pivot.theaterId = form.theater_id.data
        pivot.internalId = form.internal_id.data
        db.session.add(pivot)
        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot = providers_models.AllocinePivot.query.filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()

        venue_provider = providers_models.AllocineVenueProvider.query.join(
            providers_models.AllocinePivot,
            providers_models.AllocineVenueProvider.internalId == pivot.internalId,
        ).one_or_none()

        if venue_provider and venue_provider.isActive:
            return False

        if pivot.venue:
            history_api.add_action(
                action_type=history_models.ActionType.PIVOT_DELETED,
                author=current_user,
                venue=pivot.venue,
                comment=f"Pivot {cls.pivot_name()}",
            )

        if venue_provider:
            db.session.delete(venue_provider)
        db.session.delete(pivot)
        return True

    @staticmethod
    def get_cinema_id(form: forms.EditPivotForm) -> str:
        return form.theater_id.data
