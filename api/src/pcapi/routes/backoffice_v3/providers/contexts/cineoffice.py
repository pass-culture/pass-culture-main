import typing

from pcapi.core.providers import models as providers_models
from pcapi.models import db

from .. import forms
from .base import ProviderContext


class CineofficeContext(ProviderContext):
    @classmethod
    def provider_class(cls) -> typing.Type:
        return providers_models.CDSCinemaDetails

    @classmethod
    def get_form(cls, provider_id: int | None = None) -> forms.EditCineOfficeForm:
        if provider_id is None:
            return forms.EditCineOfficeForm()

        provider = providers_models.CDSCinemaDetails.query.get_or_404(provider_id)
        return forms.EditCineOfficeForm(
            # TODO PC-21792
            # venue_id=[provider.venueId],
            account_id=provider.accountId,
            api_token=provider.cinemaApiToken,
        )

    @classmethod
    def create_provider(cls, form: forms.EditCineOfficeForm) -> None:
        provider = providers_models.CDSCinemaDetails(
            # TODO PC-21792
            # venueId=form.venue_id.data[0],
            accountId=form.account_id.data,
            cinemaApiToken=form.api_token.data,
        )
        db.session.add(provider)

    @classmethod
    def update_provider(cls, form: forms.EditCineOfficeForm, provider_id: int) -> None:
        provider = providers_models.CDSCinemaDetails.query.get_or_404(provider_id)
        # TODO PC-21792
        db.session.add(provider)

    @classmethod
    def delete_provider(cls, provider_id: int) -> None:
        pass  # TODO PC-21792
