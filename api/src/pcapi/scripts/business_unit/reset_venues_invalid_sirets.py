import logging

from pcapi.core.offerers.models import Venue
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)


def dump_venue(venue):
    print("----")
    print("Venue with wrong siret and bank")
    print("venue id", venue.id)
    print("venue postalCode", venue.postalCode)
    print("venue siret", venue.siret)
    print("offerer siren", venue.managingOfferer.siren)
    print("venue name", venue.name)
    print("offerer id", venue.managingOfferer.id)
    print("offerer name", venue.managingOfferer.name)
    print(
        "offerer link", f"https://pro.staging.passculture.team/accueil?structure={humanize(venue.managingOfferer.id)}"
    )


def reset_venue_siret(venue, dry_run):
    venue.comment = "SIRET invalide"
    venue.siret = None
    if not dry_run:
        logger.info(
            "Reset venue SIRET, invalid SIRET cause it doesn't include offerer SIREN",
            extra={
                "venue": venue.id,
                "siret": venue.siret,
                "siren": venue.managingOfferer.siren,
            },
        )
    return venue


def normalize_venue_postal_code(venue, dry_run):
    invalid_postal_code = venue.postalCode
    venue.postalCode = venue.postalCode.strip().replace(" ", "")
    if not dry_run:
        logger.info(
            "Normalize venue postalCode",
            extra={
                "venue": venue.id,
                "postalCode": venue.postalCode,
                "invalid_postalCode": invalid_postal_code,
            },
        )
    return venue


def reset_venues_invalid_sirets(dry_run=True):
    venues = Venue.query.filter(Venue.siret != None).all()
    have_been_dump = []
    for venue in venues:
        updated_venue = None
        if (
            venue.id not in have_been_dump
            and (venue.bankInformation is not None or venue.managingOfferer.bankInformation is not None)
            and not venue.siret.startswith(venue.managingOfferer.siren)
        ):
            updated_venue = reset_venue_siret(venue, dry_run)
        if len(venue.postalCode) != 5:
            updated_venue = normalize_venue_postal_code(venue, dry_run)
        if updated_venue:
            dump_venue(venue)
            if not dry_run:
                repository.save(updated_venue)
    if dry_run:
        print("This was a dry run, nothing have been saved")
