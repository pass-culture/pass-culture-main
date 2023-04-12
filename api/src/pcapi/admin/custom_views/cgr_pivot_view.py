import logging
import typing

import flask
from flask_admin.form import SecureForm
from werkzeug.exceptions import Forbidden
from wtforms import Form
from wtforms import IntegerField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import URL

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors.cgr import cgr
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db


logger = logging.getLogger(__name__)


class CGRPivotForm(SecureForm):
    venue_id = IntegerField("Identifiant numérique du lieu (pass Culture)", [DataRequired()])
    cinema_id = StringField("Identifiant Cinéma (CGR)", [DataRequired()])
    cinema_url = StringField("URL (CGR)", [DataRequired(), URL()])
    cinema_password = StringField("Mot de passe (CGR)", [DataRequired()])


class CGRPivotView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = [
        "cinemaProviderPivot.venue.id",
        "cinemaProviderPivot.venue.name",
        "cinemaProviderPivot.idAtProvider",
        "cinemaUrl",
        "password",
    ]
    column_searchable_list = ["cinemaProviderPivot.venue.id", "cinemaProviderPivot.idAtProvider"]
    column_sortable_list: list[str] = []
    column_labels = {
        "cinemaProviderPivot.venue.id": "Identifiant lieu (pass Culture)",
        "cinemaProviderPivot.venue.name": "Lieu",
        "cinemaProviderPivot.idAtProvider": "Identifiant cinéma (CGR)",
        "cinemaUrl": "URL du cinéma (CGR)",
        "password": "Mot de passe (CGR)",
    }
    column_filters: list[str] = []

    def get_form(self) -> typing.Type[CGRPivotForm]:
        return CGRPivotForm

    def on_form_prefill(self, form, id):  # type: ignore [no-untyped-def] # pylint:disable=redefined-builtin
        CGR_cinema_details = providers_models.CGRCinemaDetails.query.get(id)
        form.venue_id.data = CGR_cinema_details.cinemaProviderPivot.venueId
        form.venue_id.render_kw = {"readonly": True}
        form.cinema_id.data = CGR_cinema_details.cinemaProviderPivot.idAtProvider
        form.cinema_url.data = CGR_cinema_details.cinemaUrl
        form.cinema_password.data = CGR_cinema_details.password
        return form

    def get_edit_form(self) -> Form:
        form = super().get_edit_form()
        form.venue_id.disabled = True
        return form

    def validate_form(self, form: Form) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(form, CGRPivotForm):
            return super().validate_form(form)

        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=form.cinema_id.data, provider_id=cgr_provider.id
        )
        if pivot and pivot.venueId != form.venue_id.data:
            flask.flash("Cet identifiant cinéma existe déjà pour un autre lieu")
            return False

        return super().validate_form(form)

    def check_if_api_call_is_ok(self, CGR_cinema_details: providers_models.CGRCinemaDetails) -> int | None:
        try:
            response = cgr.get_seances_pass_culture(CGR_cinema_details)
            flask.flash("Connexion à l'API CGR OK.")
            return response.ObjetRetour.NumCine
        # it could be an unexpected XML parsing error
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Error while checking CGR API information", extra={"exc": exc})
        flask.flash("Connexion à l'API CGR KO.", "error")
        return None

    def update_model(
        self, form: CGRPivotForm, CGR_cinema_details: providers_models.CGRCinemaDetails
    ) -> providers_models.CGRCinemaDetails:
        if not self.can_edit:
            raise Forbidden()

        CGR_cinema_details.cinemaProviderPivot.idAtProvider = str(form.cinema_id.data)
        CGR_cinema_details.cinemaUrl = form.cinema_url.data.rstrip("/")
        CGR_cinema_details.password = form.cinema_password.data
        num_cinema = self.check_if_api_call_is_ok(CGR_cinema_details)
        if num_cinema:
            CGR_cinema_details.numCinema = num_cinema

        db.session.add(CGR_cinema_details)
        db.session.commit()

        return CGR_cinema_details

    def create_model(self, form: CGRPivotForm) -> providers_models.CGRCinemaDetails | None:
        if not self.can_create:
            raise Forbidden()
        CGR_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        if not CGR_provider:
            flask.flash("Provider CGR n'existe pas.", "error")
            return None
        venue_id = form.venue_id.data
        cinema_id = form.cinema_id.data
        cinema_url = form.cinema_url.data.rstrip("/")
        cinema_password = form.cinema_password.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            form.venue_id.errors = [f"Lieu id={venue_id} n'existe pas"]
            return None
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            form.venue_id.errors = [f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}"]
            return None

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=CGR_provider, idAtProvider=cinema_id
        )
        cgr_cinema_details = providers_models.CGRCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl=cinema_url, password=cinema_password
        )

        num_cinema = self.check_if_api_call_is_ok(cgr_cinema_details)
        if num_cinema:
            cgr_cinema_details.numCinema = num_cinema

        db.session.add(cinema_provider_pivot)
        db.session.add(cgr_cinema_details)
        db.session.commit()

        return cgr_cinema_details

    def delete_model(self, CGR_cinema_details: providers_models.CGRCinemaDetails) -> bool:
        cinema_provider_pivot = CGR_cinema_details.cinemaProviderPivot
        assert cinema_provider_pivot.venueId  # helps mypy
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            flask.flash("Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot CGR", "error")
            return False
        db.session.delete(CGR_cinema_details)
        db.session.delete(cinema_provider_pivot)
        db.session.commit()

        return True
