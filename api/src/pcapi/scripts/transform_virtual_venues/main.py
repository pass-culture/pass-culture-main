"""
Script to transform virtual venues into physical ones, meaning:

    1. the venue is not marked virtual (isVirtual) anymore
    2. the venue code changes to `VenueTypeCode.ADMINISTRATIVE`
    3. it must have a SIRET (should be its offerer HQ)
    4. it must be linked to an OffererAddress
"""

import argparse
import dataclasses
import logging

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sqla
import sqlalchemy.sql.functions as sqla_func

from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors.entreprise.backends.api_entreprise import EntrepriseBackend
from pcapi.connectors.entreprise.backends.testing import TestingBackend
from pcapi.core.geography.models import Address
from pcapi.core.geography.repository import search_addresses
from pcapi.core.offerers.api import LocationData
from pcapi.core.offerers.api import delete_venue
from pcapi.core.offerers.api import get_or_create_address
from pcapi.core.offerers.api import get_or_create_offerer_address
import pcapi.core.offerers.exceptions as offerers_exceptions
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


app.app_context().push()


class TransformVirtualVenueError(Exception):
    pass


class MissingSirenError(TransformVirtualVenueError):
    pass


class SiretNotActiveOrNotDiffusible(TransformVirtualVenueError):
    pass


@dataclasses.dataclass
class HeadQuarterInfo:
    diffusible: bool
    active: bool
    siret: str
    enseigne: str | None
    raison_sociale: str | None


# pylint: disable=abstract-method
class EntrepriseWithHeadQuartersBackend(EntrepriseBackend):
    """EntrepriseBackend with an extra function that cannot be added
    to the base module since only the script code will be imported
    inside the console job.
    """

    def get_head_quarter(self, siren: str) -> HeadQuarterInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/developpeurs/openapi#tag/Informations-generales/paths/~1v3~1insee~1sirene~1unites_legales~1diffusibles~1%7Bsiren%7D~1siege_social/get
        """
        subpath = f"/v3/insee/sirene/unites_legales/diffusibles/{siren}/siege_social"
        data = self._cached_get(subpath)["data"]

        return HeadQuarterInfo(
            siret=data["siret"],
            diffusible=self._is_diffusible(data),
            active=data["etat_administratif"] == "A",
            enseigne=data["enseigne"],
            raison_sociale=data["unite_legale"]["personne_morale_attributs"]["raison_sociale"],
        )


class EntrepriseWithHeadQuartersTestingBackend(TestingBackend):
    """EntrepriseWithHeadQuartersBackend cannot be used outside of
    staging and production environments.
    """

    def get_head_quarter(self, siren: str) -> HeadQuarterInfo:
        assert len(siren) == siren_utils.SIREN_LENGTH

        self._check_siren(siren)
        siret = siren + "09876"

        # allows to get a non-diffusible offerer in dev/testing environments: any SIRET which starts with '9'
        if not self._is_diffusible(siret):
            return HeadQuarterInfo(
                siret=siret,
                diffusible=False,
                active=self._is_active(siret),
                enseigne="[ND] Enseigne",
                raison_sociale="[ND] Raison sociale",
            )

        return HeadQuarterInfo(
            siret=siret,
            diffusible=True,
            active=self._is_active(siret),
            enseigne="Enseigne",
            raison_sociale="Raison sociale",
        )


def get_backend() -> EntrepriseWithHeadQuartersBackend | EntrepriseWithHeadQuartersTestingBackend:
    if settings.IS_PROD or settings.IS_STAGING:
        return EntrepriseWithHeadQuartersBackend()
    return EntrepriseWithHeadQuartersTestingBackend()


def get_head_quarter_info(siren: str) -> HeadQuarterInfo:
    return get_backend().get_head_quarter(siren)


def get_offerer_with_one_virtual_venue_query() -> BaseQuery:
    sub_query = (
        sqla.select(sqla_func.count(Venue.id).label("venue_count"), Venue.managingOffererId)
        .select_from(Venue)
        .group_by(Venue.managingOffererId)
        .subquery("sub_venues")
    )

    return (
        Offerer.query.filter(sub_query.c.venue_count == 1, Venue.isVirtual == True)
        .join(sub_query, sub_query.c.managingOffererId == Offerer.id)
        .join(Venue, Venue.managingOffererId == Offerer.id)
    )


def get_address(offerer: Offerer) -> Address:
    """Search address based on offerer's geographical data.

    If nothing is found, use the BAN API and create the missing address.
    """
    addresses = search_addresses(street=offerer.street or "", city=offerer.city, postal_code=offerer.postalCode)

    if addresses:
        return addresses[0]

    ban_address = api_adresse.get_address(
        address=offerer.street,
        postcode=offerer.postalCode,
        city=offerer.city,
        strict=True,
    )
    location_data = LocationData(
        street=ban_address.street,
        city=ban_address.city,
        postal_code=ban_address.postcode,
        insee_code=ban_address.citycode,
        latitude=ban_address.latitude,
        longitude=ban_address.longitude,
        ban_id=ban_address.id,
    )

    return get_or_create_address(location_data=location_data, is_manual_edition=False)


def transform_virtual_venue_to_physical_venue(venue: Venue, offerer: Offerer, dry_run: bool) -> None:
    # Fetching administrative data on the Entreprise API
    if not offerer.siren:
        raise MissingSirenError()

    head_quarter_info = get_head_quarter_info(offerer.siren[:9])

    if not (head_quarter_info.active and head_quarter_info.diffusible):
        raise SiretNotActiveOrNotDiffusible()

    # Fetching address data
    address = get_address(offerer)

    venue.street = address.street  # type: ignore[method-assign]
    venue.departementCode = address.departmentCode
    venue.postalCode = address.postalCode
    venue.city = address.city
    venue.latitude = address.latitude
    venue.longitude = address.longitude
    venue.offererAddress = get_or_create_offerer_address(offerer_id=offerer.id, address_id=address.id)
    venue.isVirtual = False
    venue.siret = head_quarter_info.siret
    venue.venueTypeCode = VenueTypeCode.ADMINISTRATIVE
    if head_quarter_info.enseigne:
        venue.publicName = head_quarter_info.enseigne
    venue.name = head_quarter_info.raison_sociale or offerer.name

    db.session.flush()

    logger.info(
        "Virtual venue transformed to a physical venue",
        extra={
            "venue": {
                "id": venue.id,
                "siret": head_quarter_info.siret,
                "name": venue.name,
                "publicName": venue.publicName,
            },
            "address": {
                "street": address.street,
                "departmentCode": address.departmentCode,
                "postalCode": address.postalCode,
                "city": address.city,
                "latitude": address.latitude,
                "longitude": address.longitude,
            },
        },
    )


@atomic()
def transform_or_delete_virtual_venue(venue: Venue, offerer: Offerer, dry_run: bool) -> None:
    if dry_run:
        mark_transaction_as_invalid()  # to rollback any transformations

    # Delete venues from offerer that are not valid
    if offerer.validationStatus not in (ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.VALIDATED):
        delete_venue(venue.id)
        logging.info(
            "Successfully deleted virtual venue", extra={"offererId": venue.managingOffererId, "venueId": venue.id}
        )
    else:
        transform_virtual_venue_to_physical_venue(venue, offerer, dry_run=dry_run)
        logging.info(
            "Successfully transformed virtual venue ", extra={"offererId": venue.managingOffererId, "venueId": venue.id}
        )


def transform_offerer_unique_virtual_venue_to_physical_venue(dry_run: bool) -> None:
    query = get_offerer_with_one_virtual_venue_query()

    for offerer in query:
        venue = Venue.query.filter(Venue.isVirtual == True, Venue.managingOffererId == offerer.id).one()
        try:
            transform_or_delete_virtual_venue(venue, offerer, dry_run)
        # DELETE ERROR
        except offerers_exceptions.CannotDeleteVenueWithBookingsException:
            logging.warning("Virtual Venue could not be deleted because it has bookings", extra={"venueId": venue.id})
        # TRANSFORMATION ERRORS
        except MissingSirenError:
            logging.warning(
                "Offerer does not have a SIREN", extra={"offererId": venue.managingOffererId, "venueId": venue.id}
            )
        except SiretNotActiveOrNotDiffusible:
            logging.warning(
                "Siret info cannot be used", extra={"offererId": venue.managingOffererId, "venueId": venue.id}
            )
        except api_adresse.AdresseException as err:
            logging.warning(
                "Failed to found address on BAN API",
                extra={
                    "venueId": venue.id,
                    "address": {
                        "street": offerer.street,
                        "city": offerer.street,
                        "postalCode": offerer.postalCode,
                    },
                    "exception": {"message": str(err), "class": err.__class__.__name__},
                },
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error(
                "Virtual Venue could not be transformed because of unexpected error",
                extra={
                    "offererId": venue.managingOffererId,
                    "venueId": venue.id,
                    "exception": {"message": str(err), "class": err.__class__.__name__},
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete virtual venues with no offer")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    transform_offerer_unique_virtual_venue_to_physical_venue(args.dry_run)
