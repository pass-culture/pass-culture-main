from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.pc_object import BaseQuery
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import string as string_utils
from pcapi.utils import urls


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
        information="Ce formulaire permet de créer une nouvelle entité juridique et le partenaire culturel associé dans la base de données. "
        "L'Acteur Culturel doit avoir créé son compte utilisateur sur PC Pro et sera ainsi rattaché à la nouvelle entité juridique. ",
        form=form,
        dst=url_for("backoffice_web.pro.create_offerer"),
        div_id="create-offerer-modal",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un partenaire culturel",
        button_text="Créer l'entité juridique",
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
        mark_transaction_as_invalid()
        return _render_get_create_offerer_form(form), 400

    pro_user = form.user
    address = form.siret_info.address
    # When non-diffusible, postal code is often [ND] but city and INSEE code are public
    postal_code = address.postal_code if string_utils.is_numeric(address.postal_code) else None

    try:
        city_info = api_adresse.get_municipality_centroid(
            address.city, postcode=postal_code, citycode=address.insee_code
        )
        if not postal_code:
            postal_code = city_info.postcode
    except api_adresse.AdresseApiException as exc:
        mark_transaction_as_invalid()
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
        phoneNumber=None,
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
        comment="Entité juridique créée depuis le backoffice",
        ds_dossier_id=form.ds_id.data,
    )
    address_body_model = offerers_schemas.AddressBodyModel(
        street=offerers_schemas.VenueAddress(address.street),
        city=offerers_schemas.VenueCity(address.city),
        postalCode=offerers_schemas.VenuePostalCode(postal_code),
        latitude=city_info.latitude,
        longitude=city_info.longitude,
        banId=city_info.id,
        label=None,
    )

    venue_creation_info = venues_serialize.PostVenueBodyModel(
        address=address_body_model,
        siret=offerers_schemas.VenueSiret(form.siret_info.siret),
        bookingEmail=offerers_schemas.VenueBookingEmail(pro_user.email),
        managingOffererId=user_offerer.offererId,
        name=offerers_schemas.VenueName(form.public_name.data),
        publicName=offerers_schemas.VenuePublicName(form.public_name.data),
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
        isOpenToPublic=False,
    )
    venue = offerers_api.create_venue(venue_creation_info, current_user)
    offerers_api.create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)

    transactional_mails.send_welcome_to_pro_email(pro_user, venue)

    flash(
        Markup("L'entité juridique et le partenaire culturel <b>{name}</b> ont été créés").format(
            name=venue.common_name
        ),
        "success",
    )
    return redirect(url_for("backoffice_web.offerer.get", offerer_id=user_offerer.offererId), code=303)


def _get_connect_as_base_query() -> BaseQuery:
    """Returns all user_id to be used as a subquery."""
    return (
        db.session.query(users_models.User)
        .with_entities(users_models.User.id)
        .join(users_models.User.UserOfferers)
        .filter(
            users_models.User.isActive.is_(True),
            ~users_models.User.has_admin_role,  # type: ignore[operator]
            ~users_models.User.has_anonymized_role,  # type: ignore[operator]
            offerers_models.UserOfferer.isValidated,
        )
    )


def _get_best_user_id_for_connect_as(query: BaseQuery) -> int | None:
    """Partial workaround to fix connect as when a user as multiple offerers.

    The workaround is to try to always select a user with only one offerer when we can
    (it is not always possible).
    """
    result = (
        db.session.query(
            offerers_models.UserOfferer.userId.label("id"),
            func.count(offerers_models.UserOfferer.offererId),
        )
        .filter(offerers_models.UserOfferer.userId.in_(query))
        .group_by(
            offerers_models.UserOfferer.userId,
        )
        .order_by(
            func.count(offerers_models.UserOfferer.offererId),
        )
        .limit(1)
        .one_or_none()
    )
    return result.id if result else None


def _check_user_for_user_id(user_id: int) -> int:
    user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one_or_none()
    if not user:
        raise NotFound()

    if not user.isActive:
        raise ValueError("L'utilisation du « connect as » n'est pas disponible pour les comptes inactifs")

    if user.has_admin_role:
        raise ValueError("L'utilisation du « connect as » n'est pas disponible pour les comptes admin")

    if user.has_anonymized_role:
        raise ValueError("L'utilisation du « connect as » n'est pas disponible pour les comptes anonymisés")

    if not (user.has_non_attached_pro_role or user.has_pro_role):
        raise ValueError("L'utilisation du « connect as » n'est disponible que pour les comptes pro")
    return user.id


def _get_user_id_from_venue_id(venue_id: int) -> int:
    query = (
        _get_connect_as_base_query()
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.Offerer.managedVenues)
        .filter(offerers_models.Venue.id == venue_id)
    )
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError("Aucun utilisateur approprié n'a été trouvé pour se connecter à ce partenaire culturel")
    return user_id


def _get_user_id_from_offerer_id(offerer_id: int) -> int:
    query = _get_connect_as_base_query().filter(offerers_models.UserOfferer.offererId == offerer_id)
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError("Aucun utilisateur approprié n'a été trouvé pour se connecter à cette entité juridique")
    return user_id


def _get_user_id_from_offer_id(offer_id: int) -> int:
    query = (
        _get_connect_as_base_query()
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.Offerer.managedVenues)
        .join(offerers_models.Venue.offers)
        .filter(offers_models.Offer.id == offer_id)
    )
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError("Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre")
    return user_id


def _get_user_id_from_collective_offer_id(offer_id: int) -> int:
    query = (
        _get_connect_as_base_query()
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.Offerer.managedVenues)
        .join(offerers_models.Venue.collectiveOffers)
        .filter(educational_models.CollectiveOffer.id == offer_id)
    )
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError("Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective")
    return user_id


def _get_user_id_from_collective_offer_template_id(offer_id: int) -> int:
    query = (
        _get_connect_as_base_query()
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.Offerer.managedVenues)
        .join(offerers_models.Venue.collectiveOfferTemplates)
        .filter(educational_models.CollectiveOfferTemplate.id == offer_id)
    )
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError(
            "Aucun utilisateur approprié n'a été trouvé pour se connecter à cette offre collective vitrine"
        )
    return user_id


def _get_user_id_from_bank_account_id(bank_account_id: int) -> int:
    query = (
        _get_connect_as_base_query()
        .join(offerers_models.UserOfferer.offerer)
        .join(offerers_models.Offerer.bankAccounts)
        .filter(finance_models.BankAccount.id == bank_account_id)
    )
    user_id = _get_best_user_id_for_connect_as(query)
    if not user_id:
        raise ValueError("Aucun utilisateur approprié n'a été trouvé pour se connecter à ce compte bancaire")
    return user_id


@pro_blueprint.route("/connect-as", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CONNECT_AS_PRO)
def connect_as() -> utils.BackofficeResponse:
    form = pro_forms.ConnectAsForm()
    if not form.validate():
        flash("Échec de la validation de sécurité, veuillez réessayer", "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.home"), code=303)

    try:
        match form.object_type.data:
            case "bank_account":
                user_id = _get_user_id_from_bank_account_id(form.object_id.data)
            case "collective_offer":
                user_id = _get_user_id_from_collective_offer_id(form.object_id.data)
            case "collective_offer_template":
                user_id = _get_user_id_from_collective_offer_template_id(form.object_id.data)
            case "offer":
                user_id = _get_user_id_from_offer_id(form.object_id.data)
            case "offerer":
                user_id = _get_user_id_from_offerer_id(form.object_id.data)
            case "venue":
                user_id = _get_user_id_from_venue_id(form.object_id.data)
            case "user":
                user_id = _check_user_for_user_id(form.object_id.data)
            case _:

                raise ValueError(
                    Markup("{object_type} non supporté pour le connect as").format(object_type=form.object_type.data)
                )
    except ValueError as exp:
        if exp.args:
            flash(exp.args[0], "warning")
        else:
            flash("Erreur inconnue", "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.home"), code=303)

    token = SecureToken(
        data=ConnectAsInternalModel(
            user_id=user_id,
            internal_admin_id=current_user.id,
            internal_admin_email=current_user.email,
            redirect_link=settings.PRO_URL + form.redirect.data,
        ).dict(),
        ttl=10,
    ).token
    return redirect(urls.build_pc_pro_connect_as_link(token), code=303)
