from gettext import gettext
from typing import Union

from flask import flash
from flask import request
from flask import url_for
from flask_admin.helpers import get_form_data
from markupsafe import Markup
from sqlalchemy.orm import query
from wtforms import BooleanField
from wtforms import DecimalField
from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.form import BaseForm
from wtforms.validators import Optional

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.providers import api
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_enabled_provider_for_pro_query
from pcapi.models import ApiErrors
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.utils.human_ids import humanize


def _venue_link(view, context, model, name) -> Markup:
    url = url_for("venue.index_view", id=model.venueId)
    text = "Lieu associé"

    return Markup(f'<a href="{url}">{text}</a>')


class VenueProviderView(BaseAdminView):
    can_edit = True
    can_create = True

    column_list = ["provider.name", "venueIdAtOfferProvider", "isActive", "provider.isActive", "lieu"]
    column_labels = {
        "provider.name": "Source de données",
        "venueIdAtOfferProvider": "Identifiant pivot (SIRET, ID Allociné …)",
        "isActive": "Import des offres et stocks activé",
        "provider.isActive": "Source de données disponible",
    }
    form_columns = ["venueId", "provider", "venueIdAtOfferProvider", "isActive"]

    form_args = dict(
        provider=dict(
            get_label="name",
        ),
        venueId=dict(
            label="ID du lieu",
        ),
    )

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(lieu=_venue_link)
        return formatters

    @staticmethod
    def _extend_query(query_to_override: query) -> query:
        venue_id = request.args.get("id")

        if venue_id:
            return query_to_override.filter(VenueProvider.venueId == venue_id)

        return query_to_override

    def scaffold_form(self) -> BaseForm:
        form_class = super().scaffold_form()
        form_class.provider = QuerySelectField(query_factory=get_enabled_provider_for_pro_query, get_label="name")
        form_class.price = DecimalField("(Exclusivement Allociné) Prix", [Optional()])
        form_class.isDuo = BooleanField("(Exclusivement Allociné) Offre duo", [Optional()])

        return form_class

    def create_model(self, form: Form) -> Union[None, VenueProvider]:
        venue_provider_body = PostVenueProviderBody(
            providerId=humanize(form.provider.data.id),
            venueId=humanize(form.venueId.data),
            isDuo=form.isDuo.data,
            price=form.price.data,
            venueIdAtOfferProvider=form.venueIdAtOfferProvider.data,
        )

        venue_provider = None

        try:
            venue_provider = api.create_venue_provider(venue_provider_body)
        except ApiErrors as e:
            for key in e.errors:
                flash(gettext(f"{key} : {e.errors[key].pop()}"), "error")

        return venue_provider

    def edit_form(self, obj=None) -> Form:
        form_class = self.get_create_form()
        form_class.venueId = None
        form_class.provider = None
        form_class.price = None
        form_class.isDuo = None

        return form_class(get_form_data(), obj=obj)
