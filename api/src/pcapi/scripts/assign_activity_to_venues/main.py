"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42163-rattapage-activite-principale-et-domaines-partenaires-ancienne-typologie-autre \
  -f NAMESPACE=assign_activity_to_venues \
  -f SCRIPT_ARGUMENTS="--activity=MUSEUM";

"""

import argparse
import csv
import logging
import os
import typing

import sqlalchemy as sa

from pcapi.core.educational.models import EducationalDomain
from pcapi.core.educational.models import EducationalDomainVenue
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.routes.backoffice.filters import ACTIVITY_MAPPING
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


FILENAME = "venues.csv"
HEADERS = {
    "venue_id": "venue_id",
    "activity": "new_category",
}

DOMAIN_MAPPING = {
    Activity.HERITAGE_SITE: ["Patrimoine"],
    Activity.LIBRARY: ["Bande dessinée", "Univers du livre, de la lecture et des écritures"],
    Activity.SCIENCE_CENTRE: ["Culture scientifique, technique et industrielle"],
    Activity.CINEMA: ["Cinéma, audiovisuel"],
    Activity.TRAVELLING_CINEMA: ["Cinéma, audiovisuel"],
    Activity.ARTISTIC_COMPANY: ["Théâtre, expression dramatique, marionnettes"],
    Activity.RECORD_STORE: ["Musique"],
    Activity.FESTIVAL: ["Musique"],
    Activity.ART_GALLERY: ["Arts visuels, arts plastiques, arts appliqués"],
    Activity.BOOKSTORE: ["Bande dessinée", "Univers du livre, de la lecture et des écritures"],
    Activity.CREATIVE_ARTS_STORE: ["Arts visuels, arts plastiques, arts appliqués"],
    Activity.MUSIC_INSTRUMENT_STORE: ["Musique"],
    Activity.DISTRIBUTION_STORE: [
        "Univers du livre, de la lecture et des écritures",
        "Arts visuels, arts plastiques, arts appliqués",
    ],
    Activity.PUBLISHING_HOUSE: ["Univers du livre, de la lecture et des écritures"],
    Activity.TOURIST_INFORMATION_CENTRE: ["Patrimoine"],
    Activity.PRESS_OR_MEDIA: ["Média et information"],
    Activity.RADIO_OR_MUSIC_STREAMING: ["Média et information"],
    Activity.PRODUCTION_OR_PROMOTION_COMPANY: ["Musique"],
    Activity.TELEVISION_OR_VIDEO_STREAMING: ["Média et information"],
}


def _read_input_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(f"{namespace_dir}/{FILENAME}", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            yield from csv_rows
    except Exception:  # pylint: disable=broad-except
        logger.warning("Use input file %s", FILENAME)
        return


def main(
    csv_input_iterator: typing.Iterator[dict[str, str]], activity: Activity, open_to_public: bool | None = None
) -> None:
    activity_full_text = ACTIVITY_MAPPING[activity]

    venue_update_params: dict[sa.orm.InstrumentedAttribute[typing.Any], typing.Any] = {Venue.activity: activity}
    if open_to_public is not None:
        venue_update_params[Venue.isOpenToPublic] = open_to_public

    requested_venue_ids = {
        int(row[HEADERS["venue_id"]]) for row in csv_input_iterator if row[HEADERS["activity"]] == activity_full_text
    }
    venue_ids = [
        venue_id
        for (venue_id,) in (
            db.session.query(Venue.id)
            .filter(
                Venue.id.in_((requested_venue_ids)),
                sa.or_(Venue.activity == Activity.NOT_ASSIGNED, Venue.activity.is_(None)),
            )
            .all()
        )
    ]
    db.session.query(Venue).filter(Venue.id.in_(venue_ids)).update(
        {Venue.activity: activity}, synchronize_session=False
    )

    if activity in DOMAIN_MAPPING:
        domain_ids = [
            domain_id
            for (domain_id,) in db.session.query(EducationalDomain.id)
            .filter(EducationalDomain.name.in_(DOMAIN_MAPPING[activity]))
            .all()
        ]
        if len(domain_ids) != len(DOMAIN_MAPPING[activity]):
            raise ValueError("Expected %s domains, only got %s" % (len(DOMAIN_MAPPING[activity]), len(domain_ids)))

        venue_domain_data = []
        for venue_id in venue_ids:
            existing_domain_ids = [
                i
                for (i,) in db.session.query(EducationalDomainVenue.educationalDomainId).filter(
                    EducationalDomainVenue.venueId == venue_id
                )
            ]
            for domain_id in set(domain_ids) - set(existing_domain_ids):
                venue_domain_data.append({"educationalDomainId": domain_id, "venueId": venue_id})
        db.session.execute(sa.insert(EducationalDomainVenue), venue_domain_data)

    logger.info(
        "Setting isOpenToPublic %s, setting activity %s, adding domains %s for %i Venues. Updated ids: %s",
        open_to_public if open_to_public else "-",
        activity.name if activity else "-",
        DOMAIN_MAPPING[activity] if activity in DOMAIN_MAPPING else "-",
        len(venue_ids),
        venue_ids if len(venue_ids) > 0 else "-",
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--activity", type=str, help="activity to set (CINEMA, PRESS_OR_MEDIA, ...)", required=True)
    parser.add_argument("--openToPublic", type=bool, help="open_to_public value - will not change if no value given")
    args = parser.parse_args()

    if args.activity:
        try:
            activity_arg = Activity[args.activity]
        except KeyError as exception:
            raise ValueError("Use a correct activity value in --activity argument") from exception

    domains_arg: set[EducationalDomain] | None = None

    with atomic():
        main(
            csv_input_iterator=_read_input_file(),
            open_to_public=args.openToPublic,
            activity=activity_arg,
        )
        if args.apply:
            logger.info("Finished")
        else:
            mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")
