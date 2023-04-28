import logging
import typing

from flask import flash

from pcapi.connectors.cgr import cgr
import pcapi.core.offerers.models as offerers_models
from pcapi.core.providers import models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


class CGRContext(PivotContext):
    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.CGRCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditCGRForm:
        return forms.EditCGRForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditCGRForm:
        pivot = providers_models.CGRCinemaDetails.query.get_or_404(pivot_id)

        form = forms.EditCGRForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            cinema_url=pivot.cinemaUrl,
            password=pivot.password,
        )
        form.venue_id.disabled = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditCGRForm) -> bool:
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        if not cgr_provider:
            flash("Provider CGR n'existe pas.", "error")
            return False

        venue_id = form.venue_id.data
        cinema_id = form.cinema_id.data
        cinema_url = form.cinema_url.data.rstrip("/")
        cinema_password = form.password.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            flash(f"Lieu id={venue_id} n'existe pas", "danger")
            return False
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue.id).one_or_none()
        if pivot:
            flash(f"Des identifiants cinéma existent déjà pour ce lieu id={venue.id}", "danger")
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=cgr_provider, idAtProvider=cinema_id
        )
        cinema_pivot = providers_models.CGRCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl=cinema_url, password=cinema_password
        )

        num_cinema = cls.check_if_api_call_is_ok(cinema_pivot)
        if num_cinema:
            cinema_pivot.numCinema = num_cinema

        db.session.add(cinema_provider_pivot)
        db.session.add(cinema_pivot)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditCGRForm, pivot_id: int) -> bool:
        pivot = providers_models.CGRCinemaDetails.query.get_or_404(pivot_id)

        if pivot.cinemaProviderPivot is None:
            flash("Le provider n'a pas de pivot", "danger")  #  Demander le message le mieux adapté
            return False
        pivot.cinemaProviderPivot.idAtProvider = form.cinema_id.data
        pivot.cinemaUrl = form.cinema_url.data.rstrip("/")
        pivot.password = form.password.data
        num_cinema = cls.check_if_api_call_is_ok(pivot)

        if num_cinema:
            pivot.numCinema = num_cinema

        db.session.add(pivot)
        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot = providers_models.CGRCinemaDetails.query.get_or_404(pivot_id)
        cinema_provider_pivot = pivot.cinemaProviderPivot
        assert cinema_provider_pivot  # helps mypy
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            flash("Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot CGR", "danger")
            return False
        db.session.delete(pivot)
        db.session.delete(cinema_provider_pivot)
        return True

    @classmethod
    def check_if_api_call_is_ok(cls, pivot: providers_models.CGRCinemaDetails) -> int | None:
        try:
            response = cgr.get_seances_pass_culture(pivot)
            flash("Connexion à l'API CGR OK.")
            return response.ObjetRetour.NumCine
        # it could be an unexpected XML parsing error
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error while checking CGR API information", extra={"exc": exc})
        flash("Connexion à l'API KO.", "danger")
        return None
