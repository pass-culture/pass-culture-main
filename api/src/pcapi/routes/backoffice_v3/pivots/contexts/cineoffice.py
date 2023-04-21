import typing

from pcapi.core.providers import models as providers_models
from pcapi.models import db

from .. import forms
from .base import PivotContext


class CineofficeContext(PivotContext):
    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.CDSCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditCineOfficeForm:
        return forms.EditCineOfficeForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditCineOfficeForm:
        pivot = providers_models.CDSCinemaDetails.query.get_or_404(pivot_id)
        return forms.EditCineOfficeForm(
            # TODO PC-21792
            # venue_id=[pivot.venueId],
            account_id=pivot.accountId,
            api_token=pivot.cinemaApiToken,
        )

    @classmethod
    def create_pivot(cls, form: forms.EditCineOfficeForm) -> bool:
        pivot = providers_models.CDSCinemaDetails(
            # TODO PC-21792
            # venueId=form.venue_id.data[0],
            accountId=form.account_id.data,
            cinemaApiToken=form.api_token.data,
        )
        db.session.add(pivot)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditCineOfficeForm, pivot_id: int) -> bool:
        pivot = providers_models.CDSCinemaDetails.query.get_or_404(pivot_id)
        # TODO PC-21792
        db.session.add(pivot)
        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        return False  # TODO PC-21792
