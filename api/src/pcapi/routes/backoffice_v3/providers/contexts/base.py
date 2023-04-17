import typing

import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.utils.clean_accents import clean_accents

from .. import forms


class ProviderContext:
    @classmethod
    def provider_class(cls) -> typing.Type:
        raise NotImplementedError()

    @classmethod
    def list_providers(cls, query_string: str | None = None) -> list:
        """
        Common implementation, except for Allocine which does not use cinemaProviderPivot
        """
        provider_class = cls.provider_class()
        query = provider_class.query.options(
            sa.orm.joinedload(provider_class.cinemaProviderPivot)
            .load_only(providers_models.CinemaProviderPivot.idAtProvider)
            .joinedload(providers_models.CinemaProviderPivot.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
            )
        )
        if query_string:
            query = query.join(provider_class.cinemaProviderPivot)
            if query_string.isnumeric():
                query = query.filter(providers_models.CinemaProviderPivot.venueId == int(query_string))
            else:
                query = query.join(providers_models.CinemaProviderPivot.venue).filter(
                    sa.or_(
                        sa.func.unaccent(offerers_models.Venue.name).ilike(f"%{clean_accents(query_string)}%"),
                        providers_models.CinemaProviderPivot.idAtProvider == query_string,
                    )
                )
        return query.all()

    @classmethod
    def get_form(cls, provider_id: int | None = None) -> forms.EditProviderForm:
        raise NotImplementedError()

    @classmethod
    def create_provider(cls, form: forms.EditProviderForm) -> None:
        raise NotImplementedError()

    @classmethod
    def update_provider(cls, form: forms.EditProviderForm, provider_id: int) -> None:
        raise NotImplementedError()

    @classmethod
    def delete_provider(cls, provider_id: int) -> None:
        raise NotImplementedError()
