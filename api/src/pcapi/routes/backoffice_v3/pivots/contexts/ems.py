from datetime import datetime
import logging

from flask import flash

from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.offerers import models as offerers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db

from .. import forms
from .base import PivotContext


logger = logging.getLogger(__name__)


class EMSContext(PivotContext):
    @classmethod
    def pivot_class(cls) -> type:
        return providers_models.EMSCinemaDetails

    @classmethod
    def get_form(cls) -> forms.EditPivotForm:
        return forms.EditEMSForm()

    @classmethod
    def get_edit_form(cls, pivot_id: int) -> forms.EditPivotForm:
        pivot: providers_models.EMSCinemaDetails = providers_models.EMSCinemaDetails.query.get_or_404(pivot_id)

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
            flash("Provider EMS n'existe pas", "error")
            return False

        venue_id = form.venue_id.data
        cinema_id = form.cinema_id.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            flash("Ce lieu n'existe pas", "error")
            return False

        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue.id).one_or_none()
        if pivot:
            flash(f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}", "danger")
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
            flash("Connexion à l'API EMS KO.", "danger")

    @classmethod
    def update_pivot(cls, form: forms.EditEMSForm, pivot_id: int) -> bool:
        pivot: providers_models.EMSCinemaDetails = providers_models.EMSCinemaDetails.query.get_or_404(pivot_id)

        if not pivot.cinemaProviderPivot:
            flash("Le provider n'a pas de pivot", "danger")
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

    @classmethod
    def delete_pivot(cls, pivot_id: int) -> bool:
        pivot = providers_models.EMSCinemaDetails.query.get_or_404(pivot_id)
        cinema_provider_pivot = pivot.cinemaProviderPivot
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            flash("Ce lieu est toujours synchronisé avec EMS, vous ne pouvez pas supprimer ce pivot.", "danger")
            return False
        db.session.delete(pivot)
        db.session.delete(cinema_provider_pivot)
        return True
