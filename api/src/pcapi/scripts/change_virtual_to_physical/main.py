"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-39942-change-unique-virtual-venue-to-permanent-physical-with-siret \
  -f NAMESPACE=change_virtual_to_physical \
  -f SCRIPT_ARGUMENTS="--commit --author-id 123";
"""

import argparse
import csv
import dataclasses
import logging
import os
import typing

from pcapi.connectors.entreprise.backends.api_entreprise import EntrepriseBackend
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.zendesk_sell import api as zendesk_sell_api
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_IDS_FILENAME = "venue_ids"
VENUE_ID_HEADER = "venue_id"


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


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _read_venue_ids(filename: str) -> list[int]:
    return [int(row[VENUE_ID_HEADER]) for row in _read_csv_file(filename)]


def transform_venue(venue: Venue, author: users_models.User) -> None:
    offerer = venue.managingOfferer
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

    offerers_api.update_venue(
        venue=venue,
        modifications=modifications,
        location_modifications={},
        author=author,
        cultural_domains=["Arts numériques"],
    )

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


def sync_external_services(venue: Venue) -> None:
    zendesk_sell_api.update_venue(venue)
    update_external_pro(venue.bookingEmail)
    logger.info("External services synced for venue", extra={"venue_id": venue.id})


@atomic()
def main(not_dry: bool, author: users_models.User) -> list[Venue]:
    if not not_dry:
        logger.info("Dry run, will be rollbacked")
        mark_transaction_as_invalid()

    venue_ids = _read_venue_ids(VENUE_IDS_FILENAME)
    logger.info("Loaded venue IDs", extra={"count": len(venue_ids)})

    processed_venues: list[Venue] = []

    for venue_id in venue_ids:
        venue = db.session.query(Venue).filter(Venue.id == venue_id).one_or_none()
        if venue is None:
            logger.warning("Venue not found, skipping", extra={"venue_id": venue_id})
            continue

        try:
            transform_venue(venue, author)
            processed_venues.append(venue)
        except CouldNotReachSireneAPI:
            logger.warning(
                "L'API Sirene est injoignable",
                extra={"offererId": venue.managingOffererId, "venueId": venue.id},
            )
        except InvalidDataFromSireneAPI:
            logger.warning(
                "Les données renvoyées par l'API Sirene ne sont pas exploitables",
                extra={"offererId": venue.managingOffererId, "venueId": venue.id},
            )
        except Exception as err:
            logger.warning(
                "Erreur lors de la transformation en venue physique",
                extra={
                    "offererId": venue.managingOffererId,
                    "venueId": venue.id,
                    "exception": {"message": str(err), "class": err.__class__.__name__},
                },
            )

    return processed_venues


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--author-id", type=int, help="Author", required=True)
    args = parser.parse_args()

    author = db.session.query(users_models.User).filter(users_models.User.id == args.author_id).one()

    venues = main(not_dry=args.commit, author=author)

    if args.commit:
        for venue in venues:
            try:
                sync_external_services(venue)
            except Exception as err:
                logger.warning(
                    "Failed to sync external services for venue",
                    extra={
                        "venue_id": venue.id,
                        "exception": {"message": str(err), "class": err.__class__.__name__},
                    },
                )
        logger.info("Script terminé avec succès")
    else:
        logger.info("Dry run terminé, rollback des données")
