import logging
import typing

from flask import flash

from pcapi import settings
from pcapi.connectors import cine_digital_service
import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db
from pcapi.utils import requests

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


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
        form = forms.EditCineOfficeForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            account_id=pivot.accountId,
            api_token=pivot.cinemaApiToken,
        )
        form.venue_id.disabled = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditCineOfficeForm) -> bool:
        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        if not cds_provider:
            flash("Provider Ciné Office n'existe pas.", "danger")
            return False
        venue_id = form.venue_id.data[0]
        account_id = form.account_id.data
        cinema_id = form.cinema_id.data
        api_token = form.api_token.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            flash(f"Lieu id={venue_id} n'existe pas", "danger")
            return False
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            flash(f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}", "danger")
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=cds_provider, idAtProvider=cinema_id
        )
        cds_cinema_details = providers_models.CDSCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, accountId=account_id, cinemaApiToken=api_token
        )

        db.session.add(cinema_provider_pivot)
        db.session.add(cds_cinema_details)

        cls.check_if_api_call_is_ok(account_id=account_id, api_token=api_token)

        return True

    @classmethod
    def update_pivot(cls, form: forms.EditCineOfficeForm, pivot_id: int) -> bool:
        pivot = providers_models.CDSCinemaDetails.query.get_or_404(pivot_id)
        account_id = form.account_id.data
        cinema_id = form.cinema_id.data
        api_token = form.api_token.data

        assert pivot.cinemaProviderPivot is not None
        pivot.cinemaProviderPivot.idAtProvider = cinema_id
        pivot.accountId = account_id
        pivot.cinemaApiToken = api_token

        db.session.add(pivot)

        cls.check_if_api_call_is_ok(account_id=account_id, api_token=api_token)

        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot = providers_models.CDSCinemaDetails.query.get_or_404(pivot_id)
        cinema_provider_pivot = pivot.cinemaProviderPivot
        assert cinema_provider_pivot  # helps mypy
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()
        if venue_provider:
            flash("Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot CDS", "danger")
            return False
        db.session.delete(pivot)
        db.session.delete(cinema_provider_pivot)

        return True

    @classmethod
    def check_if_api_call_is_ok(cls, account_id: str, api_token: str) -> None:
        try:
            cine_digital_service.get_resource(
                api_url=settings.CDS_API_URL,
                account_id=account_id,
                cinema_api_token=api_token,
                resource=cine_digital_service.ResourceCDS.RATING,
            )
            flash("Connexion à l'API OK.", "danger")
            return
        except (requests.exceptions.RequestException, cds_exceptions.CineDigitalServiceAPIException) as exc:
            logger.exception(
                "Network error on checking CDS API information", extra={"exc": exc, "account_id": account_id}
            )

        flash("Connexion à l'API KO.", "danger")
