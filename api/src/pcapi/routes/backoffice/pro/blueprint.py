import typing
from functools import partial

import sqlalchemy.orm as sa_orm
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
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.utils import urls
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


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

    fetch_rows_func: typing.Callable[[str, list[str]], sa_orm.Query]
    endpoint: str
    row_id_name: str

    @classmethod
    def get_pro_link(cls, row_id: int, form: pro_forms.ProSearchForm | None, **kwargs: typing.Any) -> str:
        if form:
            kwargs.update({cls.row_id_name: row_id, "q": form.q.data, "departments": form.departments.data})
        return url_for(cls.endpoint, **kwargs)


class UserContext(Context):
    fetch_rows_func = users_api.search_pro_account
    endpoint = "backoffice_web.pro_user.get"
    row_id_name = "user_id"


class OffererContext(Context):
    fetch_rows_func = offerers_api.search_offerer
    endpoint = "backoffice_web.offerer.get"
    row_id_name = "offerer_id"


class VenueContext(Context):
    fetch_rows_func = offerers_api.search_venue
    endpoint = "backoffice_web.venue.get"
    row_id_name = "venue_id"


class BankAccountContext(Context):
    fetch_rows_func = offerers_api.search_bank_account
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
    paginated_rows = search_utils.paginate(
        query=rows,
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


def _get_connect_as_base_query() -> sa_orm.Query:
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


def _get_best_user_id_for_connect_as(query: sa_orm.Query) -> int | None:
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
