import logging
import typing

from flask import flash
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors.cgr import cgr
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import db
from pcapi.utils.crypto import decrypt
from pcapi.utils.crypto import encrypt

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


class CGRContext(PivotContext):
    @classmethod
    def pivot_name(cls) -> str:
        return "CGR"

    @classmethod
    def pivot_class(cls) -> typing.Type:
        return providers_models.CGRCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditCGRForm:
        return forms.EditCGRForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditCGRForm:
        pivot = db.session.query(providers_models.CGRCinemaDetails).filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()

        form = forms.EditCGRForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            cinema_url=pivot.cinemaUrl,
            password=decrypt(pivot.password),
        )
        form.venue_id.readonly = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditCGRForm) -> bool:
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        if not cgr_provider:
            flash("Provider CGR n'existe pas.", "warning")
            return False

        venue_id = form.venue_id.data[0]
        cinema_id = form.cinema_id.data
        cinema_url = form.cinema_url.data.rstrip("/")
        cinema_password = form.password.data

        venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
        if not venue:
            flash(Markup("Le partenaire culturel id={venue_id} n'existe pas").format(venue_id=venue_id), "warning")
            return False
        pivot = db.session.query(providers_models.CinemaProviderPivot).filter_by(venueId=venue.id).one_or_none()
        if pivot:
            flash(
                Markup("Des identifiants cinéma existent déjà pour ce partenaire culturel id={venue.id}").format(
                    venue_id=venue_id
                ),
                "warning",
            )
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=cgr_provider, idAtProvider=cinema_id
        )
        cinema_pivot = providers_models.CGRCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl=cinema_url,
            password=encrypt(cinema_password),
        )

        num_cinema = cls.check_if_api_call_is_ok(cinema_pivot)
        if num_cinema:
            cinema_pivot.numCinema = num_cinema

        db.session.add(cinema_provider_pivot)
        db.session.add(cinema_pivot)
        return True

    @classmethod
    def update_pivot(cls, form: forms.EditCGRForm, pivot_id: int) -> bool:
        pivot = db.session.query(providers_models.CGRCinemaDetails).filter_by(id=pivot_id).one_or_none()
        if not pivot:
            raise NotFound()

        if pivot.cinemaProviderPivot is None:
            flash("Le provider n'a pas de pivot", "warning")  #  Demander le message le mieux adapté
            return False
        pivot.cinemaProviderPivot.idAtProvider = form.cinema_id.data
        pivot.cinemaUrl = form.cinema_url.data.rstrip("/")
        pivot.password = encrypt(form.password.data)
        num_cinema = cls.check_if_api_call_is_ok(pivot)

        if num_cinema:
            pivot.numCinema = num_cinema

        db.session.add(pivot)
        return True

    @classmethod
    def check_if_api_call_is_ok(cls, pivot: providers_models.CGRCinemaDetails) -> int | None:
        try:
            response = cgr.get_seances_pass_culture(pivot)
            flash("Connexion à l'API CGR OK.", "success")
            return response.ObjetRetour.NumCine
        # it could be an unexpected XML parsing error
        except Exception as exc:
            logger.exception("Error while checking CGR API information", extra={"exc": exc})
        flash("Connexion à l'API KO.", "warning")
        return None
