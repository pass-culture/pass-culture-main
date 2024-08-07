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


class PivotContext:
    @classmethod
    def pivot_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def pivot_class(cls) -> typing.Type:
        raise NotImplementedError()

    @classmethod
    def list_pivots(cls, query_string: str | None = None) -> list:
        """
        Common implementation, except for Allocine which does not use cinemaProviderPivot
        """
        pivot_class = cls.pivot_class()
        query = pivot_class.query.options(
            sa.orm.joinedload(pivot_class.cinemaProviderPivot)
            .load_only(providers_models.CinemaProviderPivot.idAtProvider)
            .joinedload(providers_models.CinemaProviderPivot.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
            )
        )
        if query_string:
            query = query.join(pivot_class.cinemaProviderPivot)
            if query_string.isnumeric():
                query = query.filter(providers_models.CinemaProviderPivot.venueId == int(query_string))
            else:
                query = query.join(providers_models.CinemaProviderPivot.venue).filter(
                    sa.or_(
                        sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(
                            f"%{clean_accents(query_string)}%"
                        ),
                        providers_models.CinemaProviderPivot.idAtProvider == query_string,
                    )
                )
        return query.all()

    @classmethod
    def get_form(cls) -> forms.EditPivotForm:
        raise NotImplementedError()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditPivotForm:
        raise NotImplementedError()

    @classmethod
    def create_pivot(cls, form: forms.EditPivotForm) -> bool:
        raise NotImplementedError()

    @classmethod
    def update_pivot(cls, form: forms.EditPivotForm, pivot_id: int) -> bool:
        raise NotImplementedError()

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        """
        Common implementation except for Allocine which works differently.
        """
        pivot_name = cls.pivot_name()
        pivot_model = cls.pivot_class()
        pivot = (
            pivot_model.query.options(
                sa.orm.joinedload(pivot_model.cinemaProviderPivot).joinedload(
                    providers_models.CinemaProviderPivot.venue
                )
            )
            .filter_by(id=pivot_id)
            .one_or_none()
        )
        if not pivot:
            raise NotFound()
        cinema_provider_pivot = pivot.cinemaProviderPivot
        assert cinema_provider_pivot  # helps mypy

        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            return False

        if cinema_provider_pivot.venue:
            history_api.add_action(
                action_type=history_models.ActionType.PIVOT_DELETED,
                author=current_user,
                venue=cinema_provider_pivot.venue,
                comment=f"Pivot {pivot_name}",
            )

        db.session.delete(pivot)
        db.session.delete(cinema_provider_pivot)
        return True

    @staticmethod
    def get_cinema_id(form: forms.EditPivotForm) -> str:
        return form.cinema_id.data
