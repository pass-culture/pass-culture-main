from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup

from pcapi.connectors import api_adresse
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize


pro_blueprint = utils.child_backoffice_blueprint(
    "pro",
    __name__,
    url_prefix="/pro",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


class Context:
    """
    Pro section handles different types of entities: pro users, offerers
    and venues. Each one has its own context to handle its specificities
    """

    fetch_rows_func: typing.Callable[[str, list[str]], BaseQuery]
    get_item_base_query: typing.Callable[[int], BaseQuery]
    endpoint: str
    row_id_name: str

    @classmethod
    def get_pro_link(cls, row_id: int, form: pro_forms.ProSearchForm | None, **kwargs: typing.Any) -> str:
        if form:
            kwargs.update({cls.row_id_name: row_id, "q": form.q.data, "departments": form.departments.data})
        return url_for(cls.endpoint, **kwargs)


class UserContext(Context):
    fetch_rows_func = users_api.search_pro_account
    get_item_base_query = users_api.get_pro_account_base_query
    endpoint = "backoffice_web.pro_user.get"
    row_id_name = "user_id"


class OffererContext(Context):
    fetch_rows_func = offerers_api.search_offerer
    get_item_base_query = offerers_api.get_offerer_base_query
    endpoint = "backoffice_web.offerer.get"
    row_id_name = "offerer_id"


class VenueContext(Context):
    fetch_rows_func = offerers_api.search_venue
    get_item_base_query = offerers_api.get_venue_base_query
    endpoint = "backoffice_web.venue.get"
    row_id_name = "venue_id"


class BankAccountContext(Context):
    fetch_rows_func = offerers_api.search_bank_account
    get_item_base_query = offerers_api.get_bank_account_base_query
    endpoint = "backoffice_web.bank_account.get"
    row_id_name = "bank_account_id"

    @classmethod
    def get_pro_link(cls, row_id: int, form: pro_forms.ProSearchForm | None, **kwargs: typing.Any) -> str:
        # No ConsultCard logged for bank account
        filtered_kwargs = {k: v for k, v in kwargs.items() if v and k not in ("search_rank", "total_items")}
        return super().get_pro_link(row_id, form, **filtered_kwargs)


def render_search_template(form: pro_forms.ProSearchForm | None = None) -> str:
    if form is None:
        preferences = current_user.backoffice_profile.preferences
        form = pro_forms.ProSearchForm(departments=preferences.get("departments", []))

    return render_template("pro/search.html", title="Recherche pro", dst=url_for(".search_pro"), form=form)


@pro_blueprint.route("/search", methods=["GET"])
def search_pro() -> utils.BackofficeResponse:
    """
    Renders two search pages: first the one with the search form, then
    the one of the results.
    """
    if not request.args:
        return render_search_template()

    form = pro_forms.ProSearchForm(request.args)
    if not form.validate():
        return render_search_template(form), 400

    result_type = form.pro_type.data
    context = get_context(result_type)
    rows = context.fetch_rows_func(form.q.data, form.departments.data)
    paginated_rows = rows.paginate(
        page=form.page.data,
        per_page=form.per_page.data,
    )

    next_page = partial(url_for, ".search_pro", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, form.page.data, paginated_rows.pages)

    utils.log_backoffice_tracking_data(
        event_name="PerformSearch",
        extra_data={
            "searchType": "ProSearch",
            "searchQuery": form.q.data,
            "searchDepartments": ",".join(form.departments.data),
            "searchNbResults": paginated_rows.total,
            "searchProType": form.pro_type.data.value,
        },
    )

    if paginated_rows.total == 1:
        return redirect(
            context.get_pro_link(paginated_rows.items[0].id, form=form, search_rank=1, total_items=1), code=303
        )

    search_form = pro_forms.CompactProSearchForm(request.args)
    search_form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)
    search_form.pro_type.data = form.pro_type.data.name  # Don't send an enum to jinja

    return render_template(
        "pro/search_result.html",
        search_form=search_form,
        search_dst=url_for(".search_pro"),
        result_type=result_type.value,
        next_pages_urls=next_pages_urls,
        get_link_to_detail=context.get_pro_link,
        rows=paginated_rows,
    )


def get_context(pro_type: pro_forms.TypeOptions) -> type[Context]:
    return {
        pro_forms.TypeOptions.USER: UserContext,
        pro_forms.TypeOptions.OFFERER: OffererContext,
        pro_forms.TypeOptions.VENUE: VenueContext,
        pro_forms.TypeOptions.BANK_ACCOUNT: BankAccountContext,
    }[pro_type]


def _render_get_create_offerer_form(form: pro_forms.CreateOffererForm) -> str:
    return render_template(
        "components/turbo/modal_form.html",
        information="Ce formulaire permet de créer une nouvelle structure et le lieu associé dans la base de données. "
        "L'Acteur Culturel doit avoir créé son compte utilisateur sur PC Pro et sera ainsi rattaché à la nouvelle structure. ",
        form=form,
        dst=url_for("backoffice_web.pro.create_offerer"),
        div_id="create-offerer-modal",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer une structure",
        button_text="Créer la structure",
        data_turbo=True,
    )


@pro_blueprint.route("/create", methods=["GET"])
@utils.permission_required(perm_models.Permissions.CREATE_PRO_ENTITY)
def get_create_offerer_form() -> utils.BackofficeResponse:
    form = pro_forms.CreateOffererForm()
    return _render_get_create_offerer_form(form)


@pro_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CREATE_PRO_ENTITY)
def create_offerer() -> utils.BackofficeResponse:
    form = pro_forms.CreateOffererForm()
    if not form.validate():
        return _render_get_create_offerer_form(form), 400

    pro_user = form.user
    address = form.siret_info.address
    # When non-diffusible, postal code is often [ND] but city and INSEE code are public
    postal_code = address.postal_code if address.postal_code.isnumeric() else None

    try:
        city_info = api_adresse.get_municipality_centroid(
            address.city, postcode=postal_code, citycode=address.insee_code
        )
        if not postal_code:
            postal_code = city_info.postcode
    except api_adresse.AdresseApiException as exc:
        flash(
            Markup(
                "Une erreur s'est produite lors de la recherche des coordonnées pour <b>{code} {city}</b> : {error}"
            ).format(code=address.insee_code, city=address.city, error=str(exc))
        )
        return _render_get_create_offerer_form(form), 400

    offerer_creation_info = offerers_serialize.CreateOffererQueryModel(
        siren=form.siret_info.siret[:9],
        name=form.public_name.data,
        street=address.street,  # [ND]
        postalCode=postal_code,
        city=address.city,
        latitude=city_info.latitude,
        longitude=city_info.longitude,
    )

    new_onboarding_info = offerers_api.NewOnboardingInfo(
        target=offerers_models.Target(form.target.data),
        venueTypeCode=form.venue_type_code.data,
        webPresence=form.web_presence.data,
    )

    user_offerer = offerers_api.create_offerer(
        pro_user,
        offerer_creation_info,
        new_onboarding_info,
        author=current_user,
        comment="Structure créée depuis le backoffice",
        ds_dossier_id=form.ds_id.data,
    )

    venue_creation_info = venues_serialize.PostVenueBodyModel(
        siret=form.siret_info.siret,  # type: ignore[arg-type]
        street=address.street,  # type: ignore[arg-type]
        banId=city_info.id,  # type: ignore[arg-type]
        bookingEmail=pro_user.email,  # type: ignore[arg-type]
        city=address.city,  # type: ignore[arg-type]
        latitude=city_info.latitude,
        longitude=city_info.longitude,
        managingOffererId=user_offerer.offererId,
        name=form.public_name.data,
        publicName=form.public_name.data,
        postalCode=postal_code,  # type: ignore[arg-type]
        venueLabelId=None,
        venueTypeCode=form.venue_type_code.data,
        withdrawalDetails=None,
        description=None,
        contact=None,
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        comment=None,
    )
    venue = offerers_api.create_venue(venue_creation_info)
    offerers_api.create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)

    transactional_mails.send_welcome_to_pro_email(pro_user, venue)

    flash(Markup("La structure et le lieu <b>{name}</b> ont été créés").format(name=venue.common_name), "success")
    return redirect(url_for("backoffice_web.offerer.get", offerer_id=user_offerer.offererId), code=303)
