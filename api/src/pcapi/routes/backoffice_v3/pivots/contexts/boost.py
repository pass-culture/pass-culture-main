import typing

from pcapi.core.providers import models as providers_models
from pcapi.models import db

from .. import forms
from .base import PivotContext


class BoostContext(PivotContext):
    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.BoostCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditBoostForm:
        return forms.EditBoostForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditBoostForm:
        pivot = providers_models.BoostCinemaDetails.query.get_or_404(pivot_id)
        return forms.EditBoostForm(
            # TODO PC-21791
            # venue_id=[pivot.venueId],
            username=pivot.username,
            password=pivot.password,
            cinema_url=pivot.cinemaUrl,
        )

    @classmethod
    def create_pivot(cls, form: forms.EditBoostForm) -> bool:
        pivot = providers_models.BoostCinemaDetails(
            # TODO PC-21791
            # venueId=form.venue_id.data[0],
            username=form.username.data,
            password=form.password.data,
            cinemaUrl=form.cinema_url.data,
        )
        db.session.add(pivot)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditBoostForm, pivot_id: int) -> bool:
        pivot = providers_models.BoostCinemaDetails.query.get_or_404(pivot_id)
        # TODO PC-21791
        pivot.venueId = form.venue_id.data[0]
        pivot.username = form.username.data
        pivot.password = form.password.data
        pivot.cinemaUrl = form.cinema_url.data
        db.session.add(pivot)
        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        return False  # TODO PC-21791
