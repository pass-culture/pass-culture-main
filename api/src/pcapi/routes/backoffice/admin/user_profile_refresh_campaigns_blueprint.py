from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from sqlalchemy import orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.admin import forms
from pcapi.utils import date as date_utils


user_profile_refresh_campaigns_blueprint = utils.child_backoffice_blueprint(
    "user_profile_refresh_campaigns",
    __name__,
    url_prefix="/admin/user-profile-refresh-campaigns",
    permission=perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN,
)


def _deactivate_existing_campaigns(excluded_campaign_id: int) -> list[int]:
    filters = [users_models.UserProfileRefreshCampaign.isActive == True]
    if excluded_campaign_id is not None:
        filters.append(users_models.UserProfileRefreshCampaign.id != excluded_campaign_id)
    deactivated_campaign_ids = []
    campaigns_to_deactivate = db.session.query(users_models.UserProfileRefreshCampaign).filter(*filters).all()
    for campaign_to_deactivate in campaigns_to_deactivate:
        deactivated_campaign_ids.append(campaign_to_deactivate.id)
        campaign_to_deactivate.isActive = False
        db.session.add(campaign_to_deactivate)
        history_api.add_action(
            history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED,
            author=current_user,
            user_profile_refresh_campaign=campaign_to_deactivate,
            comment=f"Désactivation suite à l'activation de la campagne #{excluded_campaign_id}",
            modified_info={"isActive": {"old_info": True, "new_info": False}},
        )

    return deactivated_campaign_ids


@user_profile_refresh_campaigns_blueprint.route("", methods=["GET"])
def list_campaigns() -> utils.BackofficeResponse:
    creation_form = forms.UserProfileRefreshCampaignForm()
    campaigns = (
        db.session.query(users_models.UserProfileRefreshCampaign)
        .options(sa_orm.joinedload(users_models.UserProfileRefreshCampaign.action_history))
        .order_by(users_models.UserProfileRefreshCampaign.id)
        .all()
    )

    return render_template(
        "admin/user_profile_refresh_campaigns/list.html",
        creation_form=creation_form,
        rows=campaigns,
    )


@user_profile_refresh_campaigns_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN)
def create_campaign() -> utils.BackofficeResponse:
    form = forms.UserProfileRefreshCampaignForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer or url_for("backoffice_web.user_profile_refresh_campaigns.list_campaigns"),
            code=303,
        )

    new_campaign_is_active = bool(form.is_active.data)
    campaign = users_models.UserProfileRefreshCampaign(
        campaignDate=date_utils.datetime_to_localized_datetime(form.campaign_date.data),
        isActive=new_campaign_is_active,
    )
    db.session.add(campaign)
    db.session.flush()
    if new_campaign_is_active:
        _deactivate_existing_campaigns(campaign.id)
    history_api.add_action(
        history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED,
        author=current_user,
        user_profile_refresh_campaign=campaign,
        modified_info={"isActive": {"new_info": new_campaign_is_active}},
    )
    db.session.flush()
    flash("Campagne de mise à jour de données créée avec succès.", "success")

    return redirect(url_for("backoffice_web.user_profile_refresh_campaigns.list_campaigns"), code=303)


@user_profile_refresh_campaigns_blueprint.route("/<int:campaign_id>/edit_form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN)
def get_campaign_edit_form(campaign_id: int) -> utils.BackofficeResponse:
    campaign = db.session.query(users_models.UserProfileRefreshCampaign).filter_by(id=campaign_id).one_or_none()
    if not campaign:
        raise NotFound()

    form = forms.UserProfileRefreshCampaignForm()
    form.is_active.data = campaign.isActive
    form.campaign_date.data = date_utils.default_timezone_to_local_datetime(
        campaign.campaignDate, date_utils.METROPOLE_TIMEZONE
    ).replace(tzinfo=None)

    return render_template(
        "components/dynamic/modal_form.html",
        alert="L'activation de la campagne actuelle désactivera toutes les autres campagnes.",
        target_id=f"#campaign-row-{campaign_id}",
        form=form,
        dst=url_for("backoffice_web.user_profile_refresh_campaigns.edit_campaign", campaign_id=campaign_id),
        div_id=f"edit-campaign-modal-{campaign_id}",
        title=f"Modification de la campagne #{campaign_id}",
        button_text="Valider",
        ajax_redirect=True,
    )


@user_profile_refresh_campaigns_blueprint.route("/<int:campaign_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN)
def edit_campaign(campaign_id: int) -> utils.BackofficeResponse:
    campaign = db.session.query(users_models.UserProfileRefreshCampaign).filter_by(id=campaign_id).one_or_none()
    if not campaign:
        raise NotFound()

    form = forms.UserProfileRefreshCampaignForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    new_campaign_date = date_utils.datetime_to_localized_datetime(form.campaign_date.data).replace(tzinfo=None)
    modified_info = {}
    if campaign.isActive != form.is_active.data:
        modified_info["isActive"] = {"old_info": campaign.isActive, "new_info": form.is_active.data}
    if campaign.campaignDate != new_campaign_date:
        modified_info["campaignDate"] = {"old_info": campaign.campaignDate, "new_info": new_campaign_date}

    deactivated_campaign_ids = []
    if modified_info:
        history_api.add_action(
            history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED,
            author=current_user,
            user_profile_refresh_campaign=campaign,
            modified_info=modified_info,
        )
        campaign.isActive = form.is_active.data
        campaign.campaignDate = new_campaign_date
        db.session.add(campaign)
        if campaign.isActive:
            deactivated_campaign_ids = _deactivate_existing_campaigns(campaign_id)

        db.session.flush()

        flash("La campagne a été mise à jour", "success")

    campaigns = (
        db.session.query(users_models.UserProfileRefreshCampaign)
        .filter(users_models.UserProfileRefreshCampaign.id.in_(deactivated_campaign_ids + [campaign_id]))
        .options(sa_orm.joinedload(users_models.UserProfileRefreshCampaign.action_history))
        .all()
    )

    return render_template("admin/user_profile_refresh_campaigns/list_rows.html", rows=campaigns)
