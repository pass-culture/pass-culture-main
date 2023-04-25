import typing

import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents

from .. import forms
from .base import ProviderContext


class AllocineContext(ProviderContext):
    @classmethod
    def provider_class(cls) -> typing.Type:
        return providers_models.AllocinePivot

    @classmethod
    def list_providers(cls, query_string: str | None = None) -> list[providers_models.AllocinePivot]:
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
                        sa.func.unaccent(offerers_models.Venue.name).ilike(f"%{clean_accents(query_string)}%"),
                        providers_models.AllocinePivot.theaterId == query_string,
                    )
                )
        return query.all()

    @classmethod
    def get_form(cls) -> forms.EditAllocineForm:
        return forms.EditAllocineForm()

    @classmethod
    def get_edit_form(cls, provider_id: int) -> forms.EditAllocineForm:
        provider = providers_models.AllocinePivot.query.get_or_404(provider_id)
        return forms.EditAllocineForm(
            venue_id=[provider.venueId],
            theater_id=provider.theaterId,
            internal_id=provider.internalId,
        )

    @classmethod
    def create_provider(cls, form: forms.EditAllocineForm) -> bool:
        provider = providers_models.AllocinePivot(
            venueId=form.venue_id.data[0],
            theaterId=form.theater_id.data,
            internalId=form.internal_id.data,
        )
        db.session.add(provider)
        return True

    @classmethod
    def update_provider(cls, form: forms.EditAllocineForm, provider_id: int) -> bool:
        provider = providers_models.AllocinePivot.query.get_or_404(provider_id)
        provider.venueId = form.venue_id.data[0]
        provider.theaterId = form.theater_id.data
        provider.internalId = form.internal_id.data
        db.session.add(provider)
        return True

    @classmethod
    def delete_provider(cls, provider_id: int) -> bool:
        # Delete Allocine provider is not allowed
        return False
