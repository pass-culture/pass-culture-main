from flask import render_template
import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models

from . import utils


providers_blueprint = utils.child_backoffice_blueprint(
    "providers",
    __name__,
    url_prefix="/pro/support/providers",
    permission=perm_models.Permissions.MANAGE_PROVIDERS,
)


@providers_blueprint.route("", methods=["GET"])
def get_providers() -> utils.BackofficeResponse:
    return render_template("providers/get.html")


@providers_blueprint.route("/details", methods=["GET"])
def get_providers_details() -> utils.BackofficeResponse:
    allocine_provider_list = providers_models.AllocinePivot.query.options(
        sa.orm.joinedload(providers_models.AllocinePivot.venue).load_only(
            offerers_models.Venue.name,
        )
    ).all()
    boost_provider_list = providers_models.BoostCinemaDetails.query.options(
        sa.orm.joinedload(providers_models.BoostCinemaDetails.cinemaProviderPivot)
        .load_only(providers_models.CinemaProviderPivot.idAtProvider)
        .joinedload(providers_models.CinemaProviderPivot.venue)
        .load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
        )
    ).all()
    cgr_provider_list = providers_models.CGRCinemaDetails.query.options(
        sa.orm.joinedload(providers_models.CGRCinemaDetails.cinemaProviderPivot)
        .load_only(providers_models.CinemaProviderPivot.idAtProvider)
        .joinedload(providers_models.CinemaProviderPivot.venue)
        .load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
        )
    ).all()
    cineoffice_provider_list = providers_models.CDSCinemaDetails.query.options(
        sa.orm.joinedload(providers_models.CDSCinemaDetails.cinemaProviderPivot)
        .load_only(providers_models.CinemaProviderPivot.idAtProvider)
        .joinedload(providers_models.CinemaProviderPivot.venue)
        .load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
        )
    ).all()
    return render_template(
        "providers/get/details.html",
        allocine_provider_list=allocine_provider_list,
        boost_provider_list=boost_provider_list,
        cgr_provider_list=cgr_provider_list,
        cineoffice_provider_list=cineoffice_provider_list,
    )
