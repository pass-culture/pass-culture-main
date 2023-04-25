import typing

from pcapi.core.providers import models as providers_models
from pcapi.models import db

from .. import forms
from .base import ProviderContext


class BoostContext(ProviderContext):
    @classmethod
    def provider_class(cls) -> typing.Type:
        return providers_models.BoostCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditBoostForm:
        return forms.EditBoostForm()

    @classmethod
    def get_edit_form(cls, provider_id: int) -> forms.EditBoostForm:
        provider = providers_models.BoostCinemaDetails.query.get_or_404(provider_id)
        return forms.EditBoostForm(
            # TODO PC-21791
            # venue_id=[provider.venueId],
            username=provider.username,
            password=provider.password,
            cinema_url=provider.cinemaUrl,
        )

    @classmethod
    def create_provider(cls, form: forms.EditBoostForm) -> bool:
        provider = providers_models.BoostCinemaDetails(
            # TODO PC-21791
            # venueId=form.venue_id.data[0],
            username=form.username.data,
            password=form.password.data,
            cinemaUrl=form.cinema_url.data,
        )
        db.session.add(provider)
        return True

    @classmethod
    def update_provider(cls, form: forms.EditBoostForm, provider_id: int) -> bool:
        provider = providers_models.BoostCinemaDetails.query.get_or_404(provider_id)
        # TODO PC-21791
        provider.venueId = form.venue_id.data[0]
        provider.username = form.username.data
        provider.password = form.password.data
        provider.cinemaUrl = form.cinema_url.data
        db.session.add(provider)
        return True

    @classmethod
    def delete_provider(cls, provider_id: int) -> bool:
        return False  # TODO PC-21791
