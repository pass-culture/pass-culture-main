"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-39942-change-unique-virtual-venue-to-permanent-physical-with-siret \
  -f NAMESPACE=change_virtual_to_physical \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import dataclasses
import logging

import sqlalchemy as sqla
import sqlalchemy.sql.functions as sqla_func
from sqlalchemy import orm as sa_orm

from pcapi.connectors.entreprise.backends.api_entreprise import EntrepriseBackend
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.zendesk_sell import api as zendesk_sell_api
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


class CouldNotReachSireneAPI(Exception):
    pass


class InvalidDataFromSireneAPI(Exception):
    pass


@dataclasses.dataclass
class HeadQuarterInfo:
    diffusible: bool
    active: bool
    siret: str
    enseigne: str | None
    raison_sociale: str | None


def get_offerer_with_one_virtual_venue_query() -> sa_orm.Query:
    sub_query = (
        sqla.select(sqla_func.count(Venue.id).label("venue_count"), Venue.managingOffererId)
        .select_from(Venue)
        .group_by(Venue.managingOffererId)
        .subquery("sub_venues")
    )

    return (
        db.session.query(Offerer)
        .filter(sub_query.c.venue_count == 1, Venue.isVirtual == True)
        .join(sub_query, sub_query.c.managingOffererId == Offerer.id)
        .join(Venue, Venue.managingOffererId == Offerer.id)
    )


class EntrepriseWithHeadQuartersBackend(EntrepriseBackend):
    """EntrepriseBackend with an extra function that cannot be added
    to the base module since only the script code will be imported
    inside the console job.
    """

    def get_head_quarter_info(self, siren: str) -> HeadQuarterInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/developpeurs/openapi#tag/Informations-generales/paths/~1v3~1insee~1sirene~1unites_legales~1diffusibles~1%7Bsiren%7D~1siege_social/get
        """
        subpath = f"/v3/insee/sirene/unites_legales/diffusibles/{siren}/siege_social"
        data = self._cached_get(subpath)["data"]

        if not data:
            raise CouldNotReachSireneAPI()
        try:
            head_quarter_info = HeadQuarterInfo(
                siret=data["siret"],
                diffusible=self._is_diffusible(data),
                active=data["etat_administratif"] == "A",
                enseigne=data["enseigne"],
                raison_sociale=data["unite_legale"]["personne_morale_attributs"]["raison_sociale"],
            )
        except Exception as e:
            raise InvalidDataFromSireneAPI(e)
        return head_quarter_info


def transform_virtual_venue_to_physical_venue(venue: Venue, offerer: Offerer, author: users_models.User) -> None:
    head_quarter_info = EntrepriseWithHeadQuartersBackend().get_head_quarter_info(offerer.siren)
    if not head_quarter_info.diffusible:
        modifications = {
            "publicName": offerer.name,
            "name": offerer.name,
            "isPermanent": True,
            "isVirtual": False,
            "siret": head_quarter_info.siret,
            "venueTypeCode": "OTHER",
            "activity": Activity.OTHER,
        }
    else:
        modifications = {
            "publicName": head_quarter_info.raison_sociale or offerer.name,
            "name": head_quarter_info.raison_sociale or offerer.name,
            "isPermanent": True,
            "isVirtual": False,
            "siret": head_quarter_info.siret,
            "venueTypeCode": "OTHER",
            "activity": Activity.OTHER,
        }
    cultural_domains = ["Arts numériques"]

    offerers_api.update_venue(
        venue=venue,
        modifications=modifications,
        location_modifications={},
        author=author,
        cultural_domains=cultural_domains,
    )

    db.session.flush()

    logger.info(
        "Virtual venue transformed to a physical venue",
        extra={
            "venue": {
                "id": venue.id,
                "siret": head_quarter_info.siret,
                "name": venue.name,
                "publicName": venue.publicName,
                "isPermanent": venue.isPermanent,
                "isVirtual": venue.isVirtual,
                "venueTypeCode": venue.venueTypeCode,
                "activity": venue.activity,
                "cultural_domains": venue.collectiveDomains,
            },
        },
    )

    zendesk_sell_api.update_venue(venue)
    update_external_pro(venue.bookingEmail)


def transform_offerer_unique_virtual_venue_to_physical_venue(author: users_models.User) -> None:
    offerers_query = get_offerer_with_one_virtual_venue_query()

    for offerer in offerers_query:
        venue = db.session.query(Venue).filter(Venue.isVirtual == True, Venue.managingOffererId == offerer.id).one()

        try:
            transform_virtual_venue_to_physical_venue(venue, offerer, author)
        except CouldNotReachSireneAPI:
            logging.warning(
                "L'API Sirene est injoignable", extra={"offererId": venue.managingOffererId, "venueId": venue.id}
            )
        except InvalidDataFromSireneAPI:
            logging.warning(
                "Les données renvoyées par l'API Sirene ne sont pas exploitables",
                extra={"offererId": venue.managingOffererId, "venueId": venue.id},
            )
        except Exception as err:
            db.session.rollback()
            logging.warning(
                "Erreur lors de la transformation en venue physique",
                extra={
                    "offererId": venue.managingOffererId,
                    "venueId": venue.id,
                    "exception": {"message": str(err), "class": err.__class__.__name__},
                },
            )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--author-id", type=int, help="Author", required=True)
    args = parser.parse_args()

    author = db.session.query(users_models.User).filter(users_models.User.id == args.author_id).one()

    transform_offerer_unique_virtual_venue_to_physical_venue(author=author)

    if args.commit:
        db.session.commit()
        logger.info("Script terminé avec succès")
    else:
        db.session.rollback()
        logger.info("Dry run terminé, rollback des données")
