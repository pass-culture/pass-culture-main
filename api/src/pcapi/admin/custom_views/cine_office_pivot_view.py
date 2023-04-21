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

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import cine_digital_service
import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class CineOfficePivotForm(SecureForm):
    venue_id = IntegerField("Identifiant numérique du lieu (pass Culture)", [DataRequired()])
    account_id = StringField("Nom de compte (CDS)", [DataRequired()])
    cinema_id = StringField("Identifiant cinéma (CDS)", [DataRequired()])
    api_token = StringField("Clé API (CDS)", [DataRequired()])


class CineOfficePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = [
        "accountId",
        "cinemaProviderPivot.venue.id",
        "cinemaProviderPivot.venue.name",
        "cinemaProviderPivot.idAtProvider",
        "cinemaApiToken",
    ]
    column_searchable_list = ["cinemaProviderPivot.venue.id", "accountId", "cinemaProviderPivot.idAtProvider"]
    column_sortable_list: list[str] = []
    column_labels = {
        "cinemaProviderPivot.venue.id": "Identifiant lieu (pass Culture)",
        "cinemaProviderPivot.venue.name": "Lieu",
        "accountId": "Nom de compte (CDS)",
        "cinemaProviderPivot.idAtProvider": "Identifiant cinéma (CDS)",
        "cinemaApiToken": "Clé API (CDS)",
    }
    column_filters: list[str] = []

    def get_form(self) -> typing.Type[CineOfficePivotForm]:
        return CineOfficePivotForm

    def on_form_prefill(self, form, id):  # type: ignore [no-untyped-def] # pylint:disable=redefined-builtin
        cds_cinema_details = providers_models.CDSCinemaDetails.query.get(id)
        form.venue_id.data = cds_cinema_details.cinemaProviderPivot.venueId
        form.venue_id.render_kw = {"readonly": True}
        form.account_id.data = cds_cinema_details.accountId
        form.cinema_id.data = cds_cinema_details.cinemaProviderPivot.idAtProvider
        form.api_token.data = cds_cinema_details.cinemaApiToken
        return form

    def get_edit_form(self) -> Form:
        form = super().get_edit_form()
        form.venue_id.disabled = True
        return form

    def validate_form(self, form: Form) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(form, CineOfficePivotForm):
            return super().validate_form(form)

        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=form.cinema_id.data, provider_id=cds_provider.id
        )
        if pivot and pivot.venueId != form.venue_id.data:
            flask.flash("Cet identifiant cinéma existe déjà pour un autre lieu")
            return False

        return super().validate_form(form)

    def check_if_api_call_is_ok(self, account_id: str, api_token: str) -> None:
        try:
            cine_digital_service.get_resource(
                api_url=settings.CDS_API_URL,
                account_id=account_id,
                cinema_api_token=api_token,
                resource=cine_digital_service.ResourceCDS.RATING,
            )
            flask.flash("Connexion à l'API OK.")
            return
        except (requests.exceptions.RequestException, cds_exceptions.CineDigitalServiceAPIException) as exc:
            logger.exception(
                "Network error on checking CDS API information", extra={"exc": exc, "account_id": account_id}
            )

        flask.flash("Connexion à l'API KO.", "error")

    def update_model(
        self, form: CineOfficePivotForm, cds_cinema_details: providers_models.CDSCinemaDetails
    ) -> providers_models.CDSCinemaDetails:
        if not self.can_edit:
            raise Forbidden()

        account_id = form.account_id.data
        cinema_id = form.cinema_id.data
        api_token = form.api_token.data

        assert cds_cinema_details.cinemaProviderPivot is not None
        cds_cinema_details.cinemaProviderPivot.idAtProvider = cinema_id
        cds_cinema_details.accountId = account_id
        cds_cinema_details.cinemaApiToken = api_token

        db.session.add(cds_cinema_details)
        db.session.commit()

        self.check_if_api_call_is_ok(account_id=account_id, api_token=api_token)

        return cds_cinema_details

    def create_model(self, form: CineOfficePivotForm) -> providers_models.CDSCinemaDetails | None:
        if not self.can_create:
            raise Forbidden()
        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        if not cds_provider:
            flask.flash("Provider Ciné Office n'existe pas.", "error")
            return None
        venue_id = form.venue_id.data
        account_id = form.account_id.data
        cinema_id = form.cinema_id.data
        api_token = form.api_token.data

        venue = offerers_models.Venue.query.get(venue_id)
        if not venue:
            form.venue_id.errors = [f"Lieu id={venue_id} n'existe pas"]
            return None
        pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue_id).one_or_none()
        if pivot:
            form.venue_id.errors = [f"Des identifiants cinéma existent déjà pour ce lieu id={venue_id}"]
            return None

        cinema_provider_pivot = providers_models.CinemaProviderPivot(
            venue=venue, provider=cds_provider, idAtProvider=cinema_id
        )
        cds_cinema_details = providers_models.CDSCinemaDetails(
            cinemaProviderPivot=cinema_provider_pivot, accountId=account_id, cinemaApiToken=api_token
        )

        db.session.add(cinema_provider_pivot)
        db.session.add(cds_cinema_details)
        db.session.commit()

        self.check_if_api_call_is_ok(account_id=account_id, api_token=api_token)

        return cds_cinema_details

    def delete_model(self, cds_cinema_details: providers_models.CDSCinemaDetails) -> bool:
        cinema_provider_pivot = cds_cinema_details.cinemaProviderPivot
        assert cinema_provider_pivot  # helps mypy
        venue_provider = providers_models.VenueProvider.query.filter_by(
            venueId=cinema_provider_pivot.venueId, providerId=cinema_provider_pivot.providerId
        ).one_or_none()
        if venue_provider:
            flask.flash("Ce lieu est toujours synchronisé avec CDS, Vous ne pouvez pas supprimer ce pivot CDS", "error")
            return False
        db.session.delete(cds_cinema_details)
        db.session.delete(cinema_provider_pivot)
        db.session.commit()

        return True
