from flask import render_template
import sqlalchemy as sa

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.routes.backoffice import utils


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


@gdpr_extract_blueprint.route("/extract", methods=["GET"])
def list_gdpr_user_data_extract() -> utils.BackofficeResponse:
    if not FeatureToggle.WIP_BENEFICIARY_EXTRACT_TOOL.is_active():
        list_gdpr_data = []
    else:
        list_gdpr_data = _get_gdpr_data()
    return render_template(
        "gdpr_user_extract_data/list_gdpr_user_extract.html",
        list_gdpr_data=list_gdpr_data,
    )
