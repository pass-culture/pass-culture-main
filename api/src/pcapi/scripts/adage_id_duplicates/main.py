"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=adage_id_duplicates \
  -f SCRIPT_ARGUMENTS="";

"""

import csv
import datetime
import logging
import os
from dataclasses import asdict
from dataclasses import dataclass

from pcapi.app import app
from pcapi.core.educational.api.adage import get_cultural_partners
from pcapi.core.educational.schemas import AdageCulturalPartner
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


@dataclass
class VenueData:
    id: int
    siret: str | None
    soft_deleted: bool
    offerer_id: int
    offerer_siren: str


@dataclass
class Result:
    adage_id: str

    venue_1: int | None = None
    siret_1: str | None = None
    soft_deleted_1: bool | None = None
    offerer_1: int | None = None
    siren_1: str | None = None

    venue_2: int | None = None
    siret_2: str | None = None
    soft_deleted_2: bool | None = None
    offerer_2: int | None = None
    siren_2: str | None = None

    synced_venue_id: int | None = None
    synced_siret: str | None = None
    venue_id_with_adage_id_to_remove: int | None = None
    siret_with_adage_id_to_remove: str | None = None
    siren_to_deactivate: str | None = None
    comment: str = ""


def get_result(adage_id: str, venues: list[VenueData], partner_by_adage_id: dict[str, AdageCulturalPartner]) -> Result:
    result = Result(adage_id=adage_id)

    if len(venues) > 2:
        result.comment = "Adage id with more than two venues"
        return result

    venue_1, venue_2 = venues

    result.venue_1 = venue_1.id
    result.siret_1 = venue_1.siret
    result.soft_deleted_1 = venue_1.soft_deleted
    result.offerer_1 = venue_1.offerer_id
    result.siren_1 = venue_1.offerer_siren

    result.venue_2 = venue_2.id
    result.siret_2 = venue_2.siret
    result.soft_deleted_2 = venue_2.soft_deleted
    result.offerer_2 = venue_2.offerer_id
    result.siren_2 = venue_2.offerer_siren

    adage_partner = partner_by_adage_id.get(adage_id)
    if adage_partner is None:
        result.comment = "Partner with adage id not found"
        return result

    # adage partner should be active and synced
    if adage_partner.actif != 1 or adage_partner.synchroPass != 1 or not adage_partner.venueId:
        result.comment = f"Adage partner is not valid: actif={adage_partner.actif}, sync={adage_partner.synchroPass}, venueId={adage_partner.venueId}"
        return result

    # find the venue corresponding to the partner
    synced_venue = next((v for v in (venue_1, venue_2) if v.id == adage_partner.venueId), None)
    if synced_venue is None:
        result.comment = (
            f"Adage partner does not match any venue: venueId={adage_partner.venueId}, siret={adage_partner.siret}"
        )
        return result

    result.synced_venue_id = synced_venue.id
    result.synced_siret = synced_venue.siret

    venue_with_adage_id_to_remove = venue_1 if synced_venue.id == venue_2.id else venue_2
    result.venue_id_with_adage_id_to_remove = venue_with_adage_id_to_remove.id
    result.siret_with_adage_id_to_remove = venue_with_adage_id_to_remove.siret

    if synced_venue.soft_deleted:
        result.comment = "Target venue is soft-deleted"

    return result


def main() -> None:
    venues_with_adage_id = (
        db.session.query(
            offerers_models.Venue.id,
            offerers_models.Venue.adageId,
            offerers_models.Venue.siret,
            offerers_models.Venue.isSoftDeleted,
            offerers_models.Offerer.id,
            offerers_models.Offerer.siren,
        )
        .join(offerers_models.Venue.managingOfferer)
        .where(offerers_models.Venue.adageId.is_not(None))
        .execution_options(include_deleted=True)
        .tuples()
    )

    venues_by_adage_id: dict[str, list[VenueData]] = {}
    for (
        venue_id,
        adage_id,
        siret,
        soft_deleted,
        offerer_id,
        offerer_siren,
    ) in venues_with_adage_id:
        assert adage_id is not None
        venue_data = VenueData(venue_id, siret, soft_deleted, offerer_id, offerer_siren)
        venues_by_adage_id.setdefault(adage_id, []).append(venue_data)

    # fetch all adage partners
    since_date = datetime.datetime(year=1970, month=1, day=1)
    partner_by_adage_id = {
        str(partner.id): partner for partner in get_cultural_partners(since_date=since_date).partners
    }

    results: list[Result] = []
    for adage_id, venues in venues_by_adage_id.items():
        # no duplicates
        if len(venues) < 2:
            continue

        result = get_result(adage_id=adage_id, venues=venues, partner_by_adage_id=partner_by_adage_id)
        results.append(result)

    # we need to check if by removing the adageId from the venue, we would set allowedOnAdage=False on the Offerer
    for result in results:
        if result.offerer_1 == result.offerer_2:
            # venues have the same Offerer -> there is still the adageId on target venue
            continue

        offerer_id_to_check = (
            result.offerer_1 if result.venue_id_with_adage_id_to_remove == result.venue_1 else result.offerer_2
        )
        offerer = (
            db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_id_to_check).one()
        )
        if not offerer.isActive or offerer.validationStatus in (
            ValidationStatus.REJECTED,
            ValidationStatus.DELETED,
            ValidationStatus.CLOSED,
        ):
            # if Offerer is inactive, we can safely remove the adageId from the Venue
            continue

        # check if offerer has another Venue with an adageId
        other_venues_with_adage_id = (
            db.session.query(offerers_models.Venue)
            .filter(
                offerers_models.Venue.managingOffererId == offerer_id_to_check,
                offerers_models.Venue.id != result.venue_id_with_adage_id_to_remove,
                offerers_models.Venue.adageId.is_not(None),
            )
            .execution_options(include_deleted=True)
        )

        if not db.session.query(other_venues_with_adage_id.exists()).scalar():
            # Offerer has no other Venue with adageId, check if there is another Adage partner for this SIREN
            siren_to_check = (
                result.siren_1 if result.venue_id_with_adage_id_to_remove == result.venue_1 else result.siren_2
            )
            assert siren_to_check is not None
            partner = next(
                (p for p in partner_by_adage_id.values() if p.siret and p.siret[:9] == siren_to_check and p.actif == 1),
                None,
            )

            if partner is None:
                result.comment += "Offerer of Venue with adageId to remove has no other Venue with adageId, and no Adage partner was found with this SIREN"
                result.siren_to_deactivate = siren_to_check

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/duplicate_adage_ids.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(Result.__dataclass_fields__))
        writer.writeheader()
        writer.writerows((asdict(r) for r in results))


if __name__ == "__main__":
    app.app_context().push()

    main()

    logger.info("Finished")
