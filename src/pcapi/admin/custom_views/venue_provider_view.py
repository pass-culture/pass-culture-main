from flask import flash
from flask import request
from flask import url_for
from flask_admin.helpers import get_form_data
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy.orm import query
from wtforms import BooleanField
from wtforms import Form
from wtforms.fields.core import IntegerField
from wtforms.form import BaseForm
from wtforms.validators import Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_enabled_providers_for_pro_query
from pcapi.repository import repository
from pcapi.workers.venue_provider_job import venue_provider_job


def _venue_link(view, context, model, name) -> Markup:
    url = url_for("venue.index_view", id=model.venueId)
    return Markup('<a href="{}">Lieu associé</a>').format(escape(url))


def _get_venue_name_and_id(venue: Venue) -> str:
    return f"{venue.name} (#{venue.id})"


class VenueProviderView(BaseAdminView):
    can_edit = True
    can_create = False
    can_delete = False

    column_list = [
        "venue.name",
        "venue.siret",
        "provider.name",
        "venueIdAtOfferProvider",
        "isActive",
        "isDuo",
        "quantity",
        "provider.isActive",
        "venue_link",
    ]
    column_labels = {
        "venue.id": "Id du lieu",
        "venue": "Lieu",
        "venue.name": "Nom du lieu",
        "venue.siret": "Siret du lieu",
        "provider.name": "Provider",
        "venueIdAtOfferProvider": "Identifiant pivot (SIRET par défaut)",
        "isActive": "Import activé",
        "isDuo": "En duo ? (Allocine seulement)",
        "quantity": "Quantité (Allocine seulement)",
        "provider.isActive": "Provider activé",
        "venue_link": "Lien",
    }

    column_default_sort = ("id", True)
    column_searchable_list = ["venue.name", "venue.siret", "provider.name"]
    column_filters = ["venue.id", "venue.name", "venue.siret", "provider.name"]
    form_columns = ["venue", "provider", "venueIdAtOfferProvider", "isActive"]
    form_extra_fields = ["allocine_is_duo", "allocine_quantity", "allocine_price"]

    form_args = dict(
        provider=dict(
            get_label="name",
        ),
        venue=dict(get_label=_get_venue_name_and_id, label="Nom du lieu"),
    )

    def edit_form(self, obj=None) -> Form:
        form_class = self.get_edit_form()
        is_allocine = isinstance(obj, AllocineVenueProvider)

        form_class.allocine_is_duo = (
            BooleanField(
                default=obj.isDuo if is_allocine else None,
                label="En duo (allociné)",
                validators=[Optional()],
            )
            if is_allocine
            else None
        )
        form_class.allocine_quantity = (
            IntegerField(
                default=obj.quantity if is_allocine else None,
                label="Quantité (allociné)",
                validators=[Optional()],
            )
            if is_allocine
            else None
        )
        form_class.allocine_price = (
            IntegerField(
                default=obj.priceRules[0].price if is_allocine and obj.priceRules else None,
                label="Prix (allociné)",
                validators=[Optional()],
            )
            if is_allocine
            else None
        )

        return form_class(get_form_data(), obj=obj)

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(venue_link=_venue_link)
        return formatters

    @staticmethod
    def _extend_query(query_to_override: query) -> query:
        venue_id = request.args.get("id")

        if venue_id:
            return query_to_override.filter(VenueProvider.venueId == venue_id)

        return query_to_override

    def scaffold_form(self) -> BaseForm:
        form_class = super().scaffold_form()
        form_class.provider = QuerySelectField(query_factory=get_enabled_providers_for_pro_query, get_label="name")

        return form_class

    def update_model(self, form: Form, model: VenueProvider) -> None:  # pylint: disable=too-many-return-statements
        if form.venue.data.id != model.venue.id:
            flash("Le lieu ne peut pas changer", "error")
            return None

        if model.provider.isAllocine:
            if form.provider.data.id != model.provider.id:
                flash("Le provider de ce lieu ne peut pas être modifié", "error")
                return None

            if form.allocine_price.data is not None or form.allocine_price.data != "":
                price_rule = AllocineVenueProviderPriceRule.query.filter_by(
                    allocineVenueProviderId=model.id
                ).one_or_none()
                if not price_rule:
                    flash("Aucun PriceRule n'a été trouvé")
                    return None
                price_rule.price = form.allocine_price.data
                repository.save(price_rule)

            if form.allocine_quantity.data is not None or form.allocine_quantity.data != "":
                model.quantity = form.allocine_quantity.data

            if form.allocine_is_duo.data is not None or form.allocine_is_duo.data != "":
                model.isDuo = form.allocine_is_duo.data

            venue_provider_job.delay(model.id)
            return super().update_model(form, model)

        if form.provider.data.id == model.provider.id:
            venue_provider_job.delay(model.id)
            return super().update_model(form, model)

        if form.provider.data.isAllocine:
            flash("Le provider ne peut pas être changé pour Allociné", "error")
            return None

        venue_provider = None
        try:
            venue_provider = api.change_venue_provider(
                model,
                form.provider.data.id,
                form.venueIdAtOfferProvider.data,
            )
            venue_provider_job.delay(venue_provider.id)
        except exceptions.VenueSiretNotRegistered as exc:
            flash(
                f"L'identifiant pivot {exc.siret} n'est pas reconnu par {exc.provider_name}.",
                "error",
            )
        except exceptions.NoSiretSpecified:
            flash("Le siret du lieu n'est pas défini, veuillez en définir un", "error")
        except exceptions.ConnexionToProviderApiFailed:
            flash("Problème de connexion à l'API du provider", "error")
        except exceptions.ProviderNotFound:
            flash("Aucun provider actif n'a été trouvé", "error")
        except exceptions.ProviderWithoutApiImplementation:
            flash("Le provider choisir n'implémente pas notre api", "error")
        except exceptions.NoAllocinePivot:
            flash("Aucun AllocinePivot n'est défini pour ce lieu", "error")
        except exceptions.NoPriceSpecified:
            flash("Il est obligatoire de saisir un prix", "error")
        except exceptions.VenueProviderException:
            flash("Le provider n'a pas pu être enregistré", "error")

        return venue_provider
