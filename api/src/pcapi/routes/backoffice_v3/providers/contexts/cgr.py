import typing

from pcapi.core.providers import models as providers_models
from pcapi.models import db

from .. import forms
from .base import ProviderContext


class CGRContext(ProviderContext):
    @classmethod
    def provider_class(cls) -> typing.Type:
        return providers_models.CGRCinemaDetails

    @classmethod
    def get_form(cls, provider_id: int | None = None) -> forms.EditCGRForm:
        if provider_id is None:
            return forms.EditCGRForm()

        provider = providers_models.CGRCinemaDetails.query.get_or_404(provider_id)
        return forms.EditCGRForm(
            venue_id=[provider.venueId],
            account_id=provider.accountId,
            api_token=provider.cinemaApiToken,
        )

    @classmethod
    def create_provider(cls, form: forms.EditCGRForm) -> None:
        provider = providers_models.CGRCinemaDetails(
            # TODO PC-21790
            # venueId=form.venue_id.data[0],
            cinemaUrl=form.cinema_url.data,
        )
        # TODO PC-21790
        db.session.add(provider)

    @classmethod
    def update_provider(cls, form: forms.EditCGRForm, provider_id: int) -> None:
        provider = providers_models.CGRCinemaDetails.query.get_or_404(provider_id)
        # TODO PC-21790
        db.session.add(provider)

    @classmethod
    def delete_provider(cls, provider_id: int) -> None:
        pass  # TODO PC-21790
