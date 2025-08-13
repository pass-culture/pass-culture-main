from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import NotFound

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.admin import forms


user_profile_refresh_campaigns_blueprint = utils.child_backoffice_blueprint(
    "user_profile_refresh_campaigns",
    __name__,
    url_prefix="/admin/user-profile-refresh-campaigns",
    permission=perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN,
)


@user_profile_refresh_campaigns_blueprint.route("", methods=["GET"])
def list_campaigns() -> utils.BackofficeResponse:
    creation_form = forms.UserProfileRefreshCampaignForm()
    campaigns = (
        db.session.query(users_models.UserProfileRefreshCampaign)
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

    campaign = users_models.UserProfileRefreshCampaign(
        campaignDate=form.campaign_date.data,
        isActive=bool(form.is_active.data),
    )
    db.session.add(campaign)
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
    form.campaign_date.data = campaign.campaignDate

    return render_template(
        "components/dynamic/modal_form.html",
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

    campaign.isActive = form.is_active.data
    campaign.campaignDate = form.campaign_date.data
    db.session.add(campaign)
    db.session.flush()

    flash("La campagne a été modifiée", "success")

    campaigns = (
        db.session.query(users_models.UserProfileRefreshCampaign)
        .filter(users_models.UserProfileRefreshCampaign.id == campaign_id)
        .all()
    )

    return render_template("admin/user_profile_refresh_campaigns/list_rows.html", rows=campaigns)
