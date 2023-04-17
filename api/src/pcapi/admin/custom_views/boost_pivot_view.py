"""
Note: Providers edition has been implemented in backoffice v3.
Do not add any new behavior here, please update directly code backoffice v3.
"""

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
from pcapi.connectors import boost
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db


logger = logging.getLogger(__name__)


class BoostPivotForm(SecureForm):
    venue_id = IntegerField("Identifiant numérique du lieu (pass Culture)", [DataRequired()])
    cinema_id = StringField("Identifiant Cinéma (Boost)", [DataRequired()])
    username = StringField("Nom d'utilisateur (Boost)", [DataRequired()])
    password = StringField("Mot de passe (Boost)", [DataRequired()])
    cinema_url = StringField("Url (Boost)", [DataRequired(), URL()])


class BoostPivotView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = [
        "cinemaProviderPivot.venue.id",
        "cinemaProviderPivot.venue.name",
        "cinemaProviderPivot.idAtProvider",
        "username",
        "password",
        "cinemaUrl",
    ]
    column_searchable_list = ["cinemaProviderPivot.venue.id", "username", "cinemaProviderPivot.idAtProvider"]
    column_sortable_list: list[str] = []
    column_labels = {
        "cinemaProviderPivot.venue.id": "Identifiant lieu (pass Culture)",
        "cinemaProviderPivot.venue.name": "Lieu",
        "cinemaProviderPivot.idAtProvider": "Identifiant cinéma (Boost)",
        "username": "Nom d'utilisateur (Boost)",
        "password": "Mot de passe (Boost)",
        "cinemaUrl": "Url du cinéma (Boost)",
    }
    column_filters: list[str] = []

    def get_form(self) -> typing.Type[BoostPivotForm]:
        return BoostPivotForm

    def on_form_prefill(self, form, id):  # type: ignore [no-untyped-def] # pylint:disable=redefined-builtin
        boost_cinema_details = providers_models.BoostCinemaDetails.query.get(id)
        form.venue_id.data = boost_cinema_details.cinemaProviderPivot.venueId
        form.venue_id.render_kw = {"readonly": True}
        form.cinema_id.data = boost_cinema_details.cinemaProviderPivot.idAtProvider
        form.cinema_url.data = boost_cinema_details.cinemaUrl
        form.username.data = boost_cinema_details.username
        form.password.data = boost_cinema_details.password
        return form

    def get_edit_form(self) -> Form:
        form = super().get_edit_form()
        form.venue_id.disabled = True
        return form

    def validate_form(self, form: Form) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(form, BoostPivotForm):
            return super().validate_form(form)

        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=form.cinema_id.data, provider_id=boost_provider.id
        )
        if pivot and pivot.venueId != form.venue_id.data:
            flask.flash("Cet identifiant cinéma existe déjà pour un autre lieu")
            return False

        return super().validate_form(form)

    def check_if_api_call_is_ok(self, boost_cinema_details: providers_models.BoostCinemaDetails) -> None:
        try:
            boost.login(boost_cinema_details, ignore_device=True)
            flask.flash("Connexion à l'API OK.")
            return
        except boost_exceptions.BoostAPIException as exc:
            logger.exception(
                "Network error on checking Boost API information",
                extra={"exc": exc, "username": boost_cinema_details.username},
            )
        flask.flash("Connexion à l'API KO.", "error")

    def update_model(
        self, form: BoostPivotForm, boost_cinema_details: providers_models.BoostCinemaDetails
    ) -> providers_models.BoostCinemaDetails:
        if not self.can_edit:
            raise Forbidden()

        boost_cinema_details.cinemaProviderPivot.idAtProvider = str(form.cinema_id.data)
        boost_cinema_details.username = form.username.data
        boost_cinema_details.password = form.password.data
        boost_cinema_details.cinemaUrl = (
            form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data
        )
        # clear token in case an existing wrong one is still non-expired
        boost_cinema_details.token = None
        boost_cinema_details.tokenExpirationDate = None

        db.session.add(boost_cinema_details)
        db.session.commit()

        self.check_if_api_call_is_ok(boost_cinema_details)

        return boost_cinema_details

    def create_model(self, form: BoostPivotForm) -> providers_models.BoostCinemaDetails | None:
        if not self.can_create:
            raise Forbidden()
        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        if not boost_provider:
            flask.flash("Provider Boost n'existe pas.", "error")
            return None
        venue_id = form.venue_id.data
        cinema_id = form.cinema_id.data
        username = form.username.data
        password = form.password.data
        cinema_url = form.cinema_url.data + "/" if not form.cinema_url.data.endswith("/") else form.cinema_url.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            form.venue_id.errors = [f"Lieu id={venue_id} n'existe pas"]
            return None
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            form.venue_id.errors = [f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}"]
            return None

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=boost_provider, idAtProvider=cinema_id
        )
        boost_cinema_details = providers_models.BoostCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl=cinema_url, username=username, password=password
        )

        db.session.add(cinema_provider_pivot)
        db.session.add(boost_cinema_details)
        db.session.commit()

        self.check_if_api_call_is_ok(boost_cinema_details)

        return boost_cinema_details

    def delete_model(self, boost_cinema_details: providers_models.BoostCinemaDetails) -> bool:
        cinema_provider_pivot = boost_cinema_details.cinemaProviderPivot
        assert cinema_provider_pivot.venueId  # helps mypy
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()

        if venue_provider:
            flask.flash(
                "Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot Boost", "error"
            )
            return False
        db.session.delete(boost_cinema_details)
        db.session.delete(cinema_provider_pivot)
        db.session.commit()

        return True
