from datetime import datetime
import logging

from flask import flash
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import db

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


class EMSContext(PivotContext):
    @classmethod
    def pivot_name(cls) -> str:
        return "EMS"

    @classmethod
    def pivot_class(cls) -> type:
        return providers_models.EMSCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditPivotForm:
        return forms.EditEMSForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditPivotForm:
        pivot: providers_models.EMSCinemaDetails = (
            db.session.query(providers_models.EMSCinemaDetails).filter_by(id=pivot_id).one_or_none()
        )
        if not pivot:
            raise NotFound()

        # help mypy
        assert pivot.cinemaProviderPivot
        assert pivot.cinemaProviderPivot.venue

        form = forms.EditEMSForm(
            venue_id=[pivot.cinemaProviderPivot.venue.id],
            cinema_id=pivot.cinemaProviderPivot.idAtProvider,
            last_version=datetime.fromtimestamp(pivot.lastVersion).strftime("%Y-%m-%d"),
        )
        form.venue_id.readonly = True
        return form

    @classmethod
    def create_pivot(cls, form: forms.EditEMSForm) -> bool:
        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        if not ems_provider:
            flash("Provider EMS n'existe pas", "warning")
            return False

        venue_id = form.venue_id.data[0]
        cinema_id = form.cinema_id.data

        venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
        if not venue:
            flash(Markup("Le partenaire culturel id={venue_id} n'existe pas").format(venue_id=venue_id), "warning")
            return False

        pivot = db.session.query(providers_models.CinemaProviderPivot).filter_by(venueId=venue.id).one_or_none()
        if pivot:
            flash(
                Markup("Des identifiants cinéma existent déjà pour ce partenaire culturel id={venue_id}").format(
                    venue_id=venue_id
                ),
                "warning",
            )
            return False

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=ems_provider, idAtProvider=cinema_id
        )
        ems_cinema_details = providers_models.EMSCinemaDetails(cinemaProviderPivot=cinema_provider_pivot)

        db.session.add(cinema_provider_pivot)
        db.session.add(ems_cinema_details)
        cls.check_if_api_call_is_ok()
        return True

    @classmethod
    def check_if_api_call_is_ok(cls) -> None:
        connector = EMSScheduleConnector()
        try:
            connector.get_schedules(version=int(datetime.utcnow().timestamp()))
            flash("Connexion à l'API EMS OK.", "success")
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error while checking EMS API information", extra={"exc": exc})
            flash("Connexion à l'API EMS KO.", "warning")

    @classmethod
    def update_pivot(cls, form: forms.EditEMSForm, pivot_id: int) -> bool:
        pivot: providers_models.EMSCinemaDetails = (
            db.session.query(providers_models.EMSCinemaDetails).filter_by(id=pivot_id).one_or_none()
        )
        if not pivot:
            raise NotFound()

        if not pivot.cinemaProviderPivot:
            flash("Le provider n'a pas de pivot", "warning")
            return False

        pivot.cinemaProviderPivot.idAtProvider = form.cinema_id.data
        if not form.last_version.data:
            last_version = 0
        else:
            last_version = int(datetime.combine(form.last_version.data, datetime.min.time()).timestamp())
        pivot.lastVersion = last_version
        cls.check_if_api_call_is_ok()

        db.session.add(pivot)
        return True
