import logging
import typing

from flask import flash
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors import boost
from pcapi.core.external_bookings.boost import exceptions as boost_exceptions
from pcapi.core.external_bookings.boost.exceptions import BoostAPIException
from pcapi.core.external_bookings.boost.exceptions import BoostInvalidTokenException
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import db
from pcapi.utils import requests

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


class BoostContext(PivotContext):
    @classmethod
    def pivot_name(cls) -> str:
        return "Boost"

    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.BoostCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditBoostForm:
        return forms.EditBoostForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditBoostForm:
        pivot = providers_models.BoostCinemaDetails.query.filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()
        form = forms.EditBoostForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            cinema_url=pivot.cinemaUrl,
        )
        form.venue_id.readonly = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditBoostForm) -> bool:
        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        if not boost_provider:
            flash("Provider Boost n'existe pas.", "warning")
            return False

        venue_id = form.venue_id.data[0]
        cinema_id = form.cinema_id.data
        cinema_url = form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data

        venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if not venue:
            flash(Markup("Le lieu id={venue_id} n'existe pas").format(venue_id=venue_id), "warning")
            return False
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            flash(
                Markup("Des identifiants cinéma existent déjà pour ce lieu id={venue_id}").format(venue_id=venue_id),
                "warning",
            )
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=boost_provider, idAtProvider=cinema_id
        )
        boost_cinema_details = providers_models.BoostCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl=cinema_url,
        )

        db.session.add(cinema_provider_pivot)
        db.session.add(boost_cinema_details)
        cls.check_if_api_call_is_ok(boost_cinema_details)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditBoostForm, pivot_id: int) -> bool:
        pivot = providers_models.BoostCinemaDetails.query.filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()
        assert pivot.cinemaProviderPivot
        pivot.cinemaProviderPivot.idAtProvider = str(form.cinema_id.data)
        pivot.cinemaUrl = form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data
        # clear token in case an existing wrong one is still non-expired
        pivot.token = None
        pivot.tokenExpirationDate = None

        db.session.add(pivot)
        cls.check_if_api_call_is_ok(pivot)
        return True

    @classmethod
    def check_if_api_call_is_ok(cls, pivot: providers_models.BoostCinemaDetails) -> None:
        try:
            boost.login(pivot, ignore_device=True)
            flash("Connexion à l'API OK.", "success")
            return
        except boost_exceptions.BoostAPIException as exc:
            logger.exception(
                "Network error on checking Boost API information",
                extra={"exc": exc, "cinema_url": pivot.cinemaUrl},
            )
        flash("Connexion à l'API KO.", "warning")

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot_model = cls.pivot_class()
        pivot = pivot_model.query.filter_by(id=pivot_id).one_or_none()

        if not pivot:
            raise NotFound()
        try:
            boost.logout(pivot)
        except (requests.exceptions.RequestException, BoostInvalidTokenException, BoostAPIException) as exc:
            logger.exception(
                "Unexpected error from Boost logout API", extra={"exc": exc, "cinema_url": pivot.cinemaUrl}
            )

        return super().delete_pivot(pivot_id)
