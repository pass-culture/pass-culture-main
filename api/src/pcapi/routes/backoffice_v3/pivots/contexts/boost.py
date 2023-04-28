import logging
import typing

from flask import flash

from pcapi.connectors import boost
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.offerers.models as offerers_models
from pcapi.core.providers import models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


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
        form = forms.EditBoostForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            cinema_url=pivot.cinemaUrl,
            username=pivot.username,
            password=pivot.password,
        )
        form.venue_id.disabled = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditBoostForm) -> bool:
        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        if not boost_provider:
            flash("Provider Boost n'existe pas.", "danger")
            return False

        venue_id = form.venue_id.data[0]
        cinema_id = form.cinema_id.data
        username = form.username.data
        password = form.password.data
        cinema_url = form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            flash(f"Lieu id={venue_id} n'existe pas", "danger")
            return False
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            flash(f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}", "danger")
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=boost_provider, idAtProvider=cinema_id
        )
        boost_cinema_details = providers_models.BoostCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl=cinema_url, username=username, password=password
        )

        db.session.add(cinema_provider_pivot)
        db.session.add(boost_cinema_details)
        cls.check_if_api_call_is_ok(boost_cinema_details)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditBoostForm, pivot_id: int) -> bool:
        pivot = providers_models.BoostCinemaDetails.query.get_or_404(pivot_id)
        assert pivot.cinemaProviderPivot
        pivot.cinemaProviderPivot.idAtProvider = str(form.cinema_id.data)
        pivot.username = form.username.data
        pivot.password = form.password.data
        pivot.cinemaUrl = form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data
        # clear token in case an existing wrong one is still non-expired
        pivot.token = None
        pivot.tokenExpirationDate = None

        db.session.add(pivot)
        cls.check_if_api_call_is_ok(pivot)
        return True

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot = providers_models.BoostCinemaDetails.query.get_or_404(pivot_id)
        cinema_provider_pivot = pivot.cinemaProviderPivot
        assert cinema_provider_pivot  # helps mypy

        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            flash("Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot Boost", "danger")
            return False

        db.session.delete(pivot)
        db.session.delete(cinema_provider_pivot)
        return True

    @classmethod
    def check_if_api_call_is_ok(cls, pivot: providers_models.BoostCinemaDetails) -> None:
        try:
            boost.login(pivot, ignore_device=True)
            flash("Connexion à l'API OK.")
            return
        except boost_exceptions.BoostAPIException as exc:
            logger.exception(
                "Network error on checking Boost API information",
                extra={"exc": exc, "username": pivot.username},
            )
        flash("Connexion à l'API KO.", "danger")
