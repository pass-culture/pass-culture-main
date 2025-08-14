import enum

from flask import flash
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from sqlalchemy import orm as sa_orm
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect

from pcapi.core.artist import models as artist_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms


artists_blueprint = utils.child_backoffice_blueprint(
    "artist",
    __name__,
    url_prefix="/catalogue/artist",
    permission=perm_models.Permissions.READ_OFFERS,
)


class ArtistDetailsActionType(enum.StrEnum):
    EDIT = enum.auto()
    BLACKLIST = enum.auto()
    LINK_PRODUCT = enum.auto()
    UNLINK_PRODUCT = enum.auto()
    MERGE = enum.auto()
    SPLIT = enum.auto()


def _get_artist_details_actions() -> dict[ArtistDetailsActionType, bool]:
    can_manage_offers = utils.has_current_user_permission(perm_models.Permissions.MANAGE_OFFERS)
    can_manage_fraud = utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS)

    actions = {
        ArtistDetailsActionType.EDIT: can_manage_offers,
        ArtistDetailsActionType.BLACKLIST: can_manage_fraud,
        ArtistDetailsActionType.LINK_PRODUCT: can_manage_offers,
        ArtistDetailsActionType.UNLINK_PRODUCT: can_manage_offers,
        ArtistDetailsActionType.MERGE: can_manage_offers,
        ArtistDetailsActionType.SPLIT: can_manage_offers,
    }
    return actions


@artists_blueprint.route("/<string:artist_id>", methods=["GET"])
def get_artist_details(artist_id: str) -> utils.BackofficeResponse:
    artist = (
        db.session.query(artist_models.Artist)
        .filter_by(id=artist_id)
        .options(
            sa_orm.joinedload(artist_models.Artist.products).options(
                sa_orm.load_only(
                    offers_models.Product.id,
                    offers_models.Product.name,
                    offers_models.Product.subcategoryId,
                )
            ),
            sa_orm.joinedload(artist_models.Artist.aliases).options(
                sa_orm.load_only(artist_models.ArtistAlias.artist_alias_name)
            ),
        )
        .one_or_none()
    )
    if not artist:
        raise NotFound()

    return render_template(
        "artists/details.html",
        artist=artist,
        allowed_actions=_get_artist_details_actions(),
        action=ArtistDetailsActionType,
    )


@artists_blueprint.route("/<string:artist_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_artist_edit_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    form = forms.ArtistEditForm(obj=artist)
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        ajax_submit=False,
        dst=url_for(".post_artist_edit_form", artist_id=artist.id),
        div_id=f"edit-artist-modal-{artist.id}",
        title=f"Éditer l'artiste {artist.name}",
        button_text="Enregistrer",
    )


@artists_blueprint.route("/<string:artist_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def post_artist_edit_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    form = forms.ArtistEditForm()
    if form.validate_on_submit():
        form.populate_obj(artist)
        flash(Markup("L'artiste <strong>{name}</strong> a été mis à jour.").format(name=artist.name), "success")
    else:
        flash(utils.build_form_error_msg(form), "warning")

    return redirect(request.referrer or url_for(".get_artist_details", artist_id=artist_id), 303)


@artists_blueprint.route("/<string:artist_id>/blacklist", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_artist_blacklist_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    form = empty_forms.EmptyForm()
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for(".post_artist_blacklist", artist_id=artist.id),
        div_id=f"blacklist-artist-modal-{artist.id}",
        title=f"Blacklister l'artiste {artist.name}",
        button_text="Confirmer",
        ajax_submit=False,
        information=Markup(
            "Vous êtes sur le point de blacklister cet artiste. Il n'apparaîtra plus sur l'application. Êtes-vous sûr de vouloir continuer ?"
        ),
    )


@artists_blueprint.route("/<string:artist_id>/blacklist", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def post_artist_blacklist(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    artist.is_blacklisted = True
    db.session.add(artist)

    flash(Markup("L'artiste <strong>{name}</strong> a été blacklisté.").format(name=artist.name), "success")
    return redirect(request.referrer or url_for(".get_artist_details", artist_id=artist_id), 303)


@artists_blueprint.route("/<string:artist_id>/unblacklist", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_artist_unblacklist_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    form = empty_forms.EmptyForm()
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for(".post_artist_unblacklist", artist_id=artist.id),
        div_id=f"unblacklist-artist-modal-{artist.id}",
        title=f"Réactiver l'artiste {artist.name}",
        button_text="Confirmer et réactiver",
        information=Markup(
            "Vous êtes sur le point de réactiver cet artiste. Il sera de nouveau visible sur l'application."
        ),
        ajax_submit=False,
    )


@artists_blueprint.route("/<string:artist_id>/unblacklist", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def post_artist_unblacklist(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    artist.is_blacklisted = False
    flash(Markup("L'artiste <strong>{name}</strong> a été réactivé.").format(name=artist.name), "success")
    return redirect(request.referrer or url_for(".get_artist_details", artist_id=artist_id), 303)


@artists_blueprint.route("/<string:artist_id>/products/<int:product_id>/unlink-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_unlink_product_form(artist_id: str, product_id: int) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
        flash("Produit non trouvé.", "warning")
        raise NotFound()

    form = empty_forms.EmptyForm()
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        div_id=f"unlink-product-modal-{product.id}",
        target_id=f"#product-row-{product.id}",
        dst=url_for(".post_unlink_product", artist_id=artist.id, product_id=product.id),
        title="Dissocier un produit",
        button_text="Confirmer la dissociation",
        information=Markup(
            "Êtes-vous sûr de vouloir supprimer le lien entre l'artiste <b>{artist_name}</b> et le produit <b>{product_name}</b> ?"
        ).format(artist_name=artist.name, product_name=product.name),
        ajax_submit=True,
    )


@artists_blueprint.route("/<string:artist_id>/products/<int:product_id>/unlink", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def post_unlink_product(artist_id: str, product_id: int) -> utils.BackofficeResponse:
    link = (
        db.session.query(artist_models.ArtistProductLink).filter_by(artist_id=artist_id, product_id=product_id).first()
    )

    if link:
        db.session.delete(link)
        flash("Le lien avec le produit a été supprimé avec succès.", "success")
        return "", 200
    else:
        flash("Le lien à supprimer n'a pas été trouvé.", "warning")
        mark_transaction_as_invalid()
        return "", 400


@artists_blueprint.route("/<string:artist_id>/associate-product", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def associate_product_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    search_form = forms.AssociateProductSearchForm()

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#associate-product-modal",
        modal_content_id="associate-product-modal",
        close_on_validation=False,
        div_id=f"associate-product-modal-{artist.id}",
        dst=url_for("backoffice_web.artist.associate_product", artist_id=artist_id),
        title="Associer un produit",
        form=search_form,
        information=Markup("Rechercher un produit via son identifiant pour l'associer à <b>{name}</b>.").format(
            name=artist.name
        ),
        button_text="Rechercher",
        is_multistep_form=True,
    )


@artists_blueprint.route("/<string:artist_id>/associate-product", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def associate_product(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    search_form = forms.AssociateProductSearchForm()

    id_type = forms.ProductIdentifierTypeEnum[search_form.identifier_type.data]
    id_value = search_form.identifier_value.data

    query = db.session.query(offers_models.Product)
    if id_type == forms.ProductIdentifierTypeEnum.EAN:
        query = query.filter_by(ean=id_value)
    elif id_type == forms.ProductIdentifierTypeEnum.ALLOCINE_ID:
        query = query.filter(offers_models.Product.extraData["allocineId"] == id_value)
    elif id_type == forms.ProductIdentifierTypeEnum.VISA:
        query = query.filter(offers_models.Product.extraData["visa"].astext == id_value)

    found_product = query.one_or_none()
    if not found_product:
        flash(
            f"Aucun produit trouvé avec l'identifiant {id_value} ({id_type.value}). Veuillez vérifier l'identifiant et réessayer.",
            "warning",
        )
        return redirect(url_for("backoffice_web.artist.associate_product_form", artist_id=artist_id))

    confirm_form = forms.ConfirmAssociationForm()
    confirm_form.product_id.data = found_product.id
    return render_template(
        "components/dynamic/modal_form.html",
        div_id=f"associate-product-modal-{artist.id}",
        dst=url_for("backoffice_web.artist.confirm_association", artist_id=artist_id),
        title="Confirmer l'association",
        form=confirm_form,
        button_text="Confirmer l'association",
        include_template="artists/associate_product_preview.html",
        ajax_submit=False,
        # for the included template
        found_product=found_product,
    )


@artists_blueprint.route("/<string:artist_id>/confirm-association", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def confirm_association(artist_id: str) -> utils.BackofficeResponse:
    confirm_form = forms.ConfirmAssociationForm()

    if confirm_form.validate_on_submit():
        product_id = confirm_form.product_id.data
        artist_type = forms.artist_models.ArtistType[confirm_form.artist_type.data]

        existing_link = (
            db.session.query(artist_models.ArtistProductLink)
            .filter_by(artist_id=artist_id, product_id=product_id)
            .first()
        )

        if existing_link:
            flash("Ce produit est déjà associé à cet artiste.", "info")
        else:
            new_link = artist_models.ArtistProductLink(
                artist_id=artist_id, product_id=product_id, artist_type=artist_type
            )
            db.session.add(new_link)
            flash("Produit associé avec succès.", "success")

    else:
        flash(utils.build_form_error_msg(confirm_form), "warning")

    return redirect(url_for("backoffice_web.artist.get_artist_details", artist_id=artist_id), 303)


@artists_blueprint.route("/<string:artist_id>/merge-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_merge_artist_form(artist_id: str) -> utils.BackofficeResponse:
    artist = db.session.query(artist_models.Artist).filter_by(id=artist_id).one_or_none()
    if not artist:
        raise NotFound()

    form = forms.MergeArtistForm(source_artist_id=artist_id)

    form.target_artist_id.endpoint_kwargs = {"source_artist_id": artist_id}

    return render_template(
        "components/dynamic/modal_form.html",
        div_id=f"merge-artist-modal-{artist.id}",
        dst=url_for(".post_merge_artists", artist_id=artist.id),
        title=f"Fusionner l'artiste {artist.name}",
        form=form,
        information=Markup(
            "L'artiste <b>{name}</b> sera conservé. Tous les produits et alias de l'artiste sélectionné seront transférés, puis cet artiste sera supprimé."
        ).format(name=artist.name),
        button_text="Confirmer la fusion",
        ajax_submit=False,
    )


@artists_blueprint.route("/<string:artist_id>/merge", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def post_merge_artists(artist_id: str) -> utils.BackofficeResponse:
    artist_to_keep_id = artist_id
    artist_to_keep = db.session.query(artist_models.Artist).filter_by(id=artist_to_keep_id).one_or_none()
    if not artist_to_keep:
        raise NotFound("L'artiste à conserver n'a pas été trouvé.")

    form = forms.MergeArtistForm(source_artist_id=artist_to_keep_id)
    if not form.validate_on_submit():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer)

    artist_to_delete_id = form.target_artist_id.data[0]
    artist_to_delete = db.session.query(artist_models.Artist).filter_by(id=artist_to_delete_id).one_or_none()
    if not artist_to_delete:
        flash("L'artiste à fusionner n'a pas été trouvé.")
        raise NotFound()

    artist_to_delete_name = artist_to_delete.name
    try:
        db.session.query(artist_models.ArtistAlias).filter_by(artist_id=artist_to_delete_id).update(
            {"artist_id": artist_to_keep_id}
        )
        db.session.query(artist_models.ArtistProductLink).filter_by(artist_id=artist_to_delete_id).update(
            {"artist_id": artist_to_keep_id}
        )
        db.session.delete(artist_to_delete)
    except Exception as err:
        flash(f"Une erreur est survenue lors de la fusion : {err}", "warning")
        mark_transaction_as_invalid()
        return redirect(url_for(".get_artist_details", artist_id=artist_to_keep))

    flash(
        Markup(
            "L'artiste <strong>{artist_to_delete_name}</strong> a été fusionné avec succès dans <strong>{artist_to_keep_name}</strong>."
        ).format(artist_to_delete_name=artist_to_delete_name, artist_to_keep_name=artist_to_keep.name),
        "success",
    )
    return redirect(url_for(".get_artist_details", artist_id=artist_to_keep.id))


@artists_blueprint.route("/<string:artist_id>/split-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_split_artist_form(artist_id: str) -> utils.BackofficeResponse:
    source_artist = (
        db.session.query(artist_models.Artist)
        .options(
            sa_orm.joinedload(artist_models.Artist.products).load_only(
                offers_models.Product.id, offers_models.Product.name
            )
        )
        .filter_by(id=artist_id)
        .one_or_none()
    )
    if not source_artist:
        raise NotFound()

    product_choices = [(p.id, p.name) for p in source_artist.products]
    form = forms.SplitArtistForm(product_choices=product_choices)

    return render_template(
        "components/dynamic/modal_form.html",
        div_id=f"split-artist-modal-{source_artist.id}",
        dst=url_for(".post_split_artist", artist_id=source_artist.id),
        title=f"Séparer l'artiste {source_artist.name}",
        form=form,
        button_text="Créer",
        ajax_submit=False,
    )


@artists_blueprint.route("/<string:artist_id>/split", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def post_split_artist(artist_id: str) -> utils.BackofficeResponse:
    source_artist = (
        db.session.query(artist_models.Artist)
        .options(
            sa_orm.joinedload(artist_models.Artist.products).load_only(
                offers_models.Product.id, offers_models.Product.name
            )
        )
        .filter_by(id=artist_id)
        .one_or_none()
    )
    if not source_artist:
        raise NotFound()

    product_choices = [(p.id, p.name) for p in source_artist.products]
    form = forms.SplitArtistForm(product_choices=product_choices, form_data=request.form)

    if not form.validate():
        context = {
            "div_id": f"split-artist-modal-{source_artist.id}",
            "dst": url_for(".post_split_artist", artist_id=source_artist.id),
            "title": f"Séparer l'artiste {source_artist.name}",
            "form": form,
            "button_text": "Créer",
        }
        return render_template("components/dynamic/modal_form.html", **context), 422

    try:
        new_artist = artist_models.Artist(name=form.new_artist_name.data, description=form.new_artist_description.data)
        db.session.add(new_artist)
        db.session.flush()

        if form.new_artist_aliases.data:
            aliases_names = [name.strip() for name in form.new_artist_aliases.data.split(",") if name.strip()]
            for alias_name in aliases_names:
                new_alias = artist_models.ArtistAlias(artist_id=new_artist.id, artist_alias_name=alias_name)
                db.session.add(new_alias)

        product_ids_to_move = form.products_to_move.data
        db.session.query(artist_models.ArtistProductLink).filter(
            artist_models.ArtistProductLink.artist_id == source_artist.id,
            artist_models.ArtistProductLink.product_id.in_(product_ids_to_move),
        ).update({"artist_id": new_artist.id}, synchronize_session=False)

    except Exception as e:
        flash(f"Une erreur est survenue lors de la séparation : {e}", "warning")
        mark_transaction_as_invalid()
        return redirect(url_for(".get_artist_details", artist_id=source_artist.id))

    flash(f'L\'artiste a été séparé avec succès. Le nouvel artiste "{new_artist.name}" a été créé.', "success")
    return redirect(url_for(".get_artist_details", artist_id=new_artist.id))
