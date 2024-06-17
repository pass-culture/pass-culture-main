from datetime import datetime
import logging

from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import url_for
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.repository import atomic
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms


logger = logging.getLogger(__name__)

gdpr_extract_blueprint = utils.child_backoffice_blueprint(
    "gdpr_extract",
    __name__,
    url_prefix="/gdpr-extract",
    permission=perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT,
)


def _get_gdpr_data() -> list[users_models.GdprUserDataExtract]:

    query = (
        users_models.GdprUserDataExtract.query.options(
            sa.orm.joinedload(users_models.GdprUserDataExtract.user).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
            sa.orm.joinedload(users_models.GdprUserDataExtract.authorUser).load_only(
                users_models.User.firstName,
                users_models.User.lastName,
            ),
        )
        .order_by(users_models.GdprUserDataExtract.id.desc())
        .filter(users_models.GdprUserDataExtract.expirationDate >= sa.func.now())
    )

    return query.all()


@gdpr_extract_blueprint.route("", methods=["GET"])
@atomic()
def list_gdpr_user_data_extract() -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_BENEFICIARY_EXTRACT_TOOL.is_active():
        list_gdpr_data = []
    else:
        list_gdpr_data = _get_gdpr_data()
    return render_template(
        "gdpr_user_extract_data/list_gdpr_user_extract.html",
        empty_form=empty_forms.EmptyForm(),
        list_gdpr_data=list_gdpr_data,
    )


@gdpr_extract_blueprint.route("/<int:extract_id>/download", methods=["POST"])
@atomic()
def download_gdpr_extract(extract_id: int) -> utils.BackofficeResponse:
    form = empty_forms.EmptyForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract"),
            code=303,
        )

    extract = (
        users_models.GdprUserDataExtract.query.filter(
            users_models.GdprUserDataExtract.id == extract_id,
            users_models.GdprUserDataExtract.expirationDate > datetime.utcnow(),  # type: ignore [operator]
        )
        .options(
            joinedload(users_models.GdprUserDataExtract.user).load_only(
                users_models.User.firstName, users_models.User.lastName
            )
        )
        .one_or_none()
    )

    if not extract:
        flash("L'extraction demandée n'existe pas ou a expiré", "warning")
        return redirect(
            url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract"),
            code=303,
        )

    try:
        files = object_storage.get_public_object(
            folder=settings.GCP_GDPR_EXTRACT_FOLDER,
            object_id=f"{extract.id}.zip",
            bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
        )
    except object_storage.FileNotFound:
        flash("L'extraction demandée existe mais aucune archive ne lui est associée", "warning")
        return redirect(
            url_for("backoffice_web.gdpr_extract.list_gdpr_user_data_extract"),
            code=303,
        )

    response = make_response(files[0])
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = f'attachment; filename="{extract.user.full_name}.zip"'
    logger.info(
        "An admin downloaded a user's data",
        extra={
            "user_id": extract.user.id,
            "extract_id": extract_id,
        },
    )

    return response
