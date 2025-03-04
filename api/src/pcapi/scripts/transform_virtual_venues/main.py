"""
Script to transform virtual venues into physical ones, meaning:

    1. the venue is not marked virtual (isVirtual) anymore
    2. the venue code changes to `VenueTypeCode.ADMINISTRATIVE`
    3. it must have a SIRET (should be its offerer HQ)
    4. it must be linked to an OffererAddress
"""

import logging
from typing import Collection

from flask_sqlalchemy import BaseQuery
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors.entreprise.backends.api_entreprise import EntrepriseBackend
from pcapi.connectors.entreprise.backends.testing import TestingBackend
from pcapi.connectors.entreprise.models import SiretInfo
from pcapi.core.geography.models import Address
from pcapi.core.geography.repository import search_addresses
from pcapi.core.offerers.api import LocationData
from pcapi.core.offerers.api import get_or_create_address
from pcapi.core.offerers.api import get_or_create_offerer_address
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.routes.public.individual_offers.v1.addresses import _get_ban_address_or_none
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


QUERY = """
select 
    venue.id
from
    venue
left join (
    select venue."managingOffererId", count(*) "venue_count" from venue
    group by venue."managingOffererId"
) as temp on temp."managingOffererId" = venue."managingOffererId"
where 
    temp."venue_count" = 1
    and venue."isVirtual" = True;
"""


class TransformVirtualVenueError(Exception):
    pass


class NotAVirtualVenue(TransformVirtualVenueError):
    pass


class MissingSirenError(TransformVirtualVenueError):
    pass


class FetchSiretError(TransformVirtualVenueError):
    pass


class FetchAddressError(TransformVirtualVenueError):
    pass


# pylint: disable=abstract-method
class EntrepriseWithHeadQuartersBackend(EntrepriseBackend):
    """EntrepriseBackend with an extra function that cannot be added
    to the base module since only the script code will be imported
    inside the console job.
    """

    def get_head_quarter(self, siren: str) -> SiretInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/developpeurs/openapi#tag/Informations-generales/paths/~1v3~1insee~1sirene~1unites_legales~1diffusibles~1%7Bsiren%7D~1siege_social/get
        """
        subpath = f"/v3/insee/sirene/unites_legales/diffusibles/{siren}/siege_social"
        data = self._cached_get(subpath)["data"]

        is_diffusible = self._is_diffusible(data)

        return SiretInfo(
            siret=data["siret"],
            active=data["etat_administratif"] == "A",
            diffusible=is_diffusible,
            name=data["enseigne"],
            address=self._get_address_from_sirene_data(data["adresse"]),
            ape_code=data["activite_principale"]["code"],
            ape_label=data["activite_principale"]["libelle"],
            legal_category_code=data["forme_juridique"]["code"],
        )


class EntrepriseWithHeadQuartersTestingBackend(TestingBackend):
    """EntrepriseWithHeadQuartersBackend cannot be used outside of
    staging and production environments.
    """

    def get_head_quarter(self, siren: str) -> SiretInfo:
        assert len(siren) == siren_utils.SIREN_LENGTH

        self._check_siren(siren)
        siret = siren + "09876"

        ape_code, ape_label = self._ape_code_and_label(siret)

        # allows to get a non-diffusible offerer in dev/testing environments: any SIRET which starts with '9'
        if not self._is_diffusible(siret):
            return SiretInfo(
                siret=siret,
                active=self._is_active(siret),
                diffusible=False,
                name="[ND]",
                address=self.nd_address,
                ape_code=ape_code,
                ape_label=ape_label,
                legal_category_code=self._legal_category_code(siret),
            )

        return SiretInfo(
            siret=siret,
            active=self._is_active(siret),
            diffusible=True,
            name="MINISTERE DE LA CULTURE",
            address=self.address,
            ape_code=ape_code,
            ape_label=ape_label,
            legal_category_code=self._legal_category_code(siret),
        )


def get_backend() -> EntrepriseWithHeadQuartersBackend | EntrepriseWithHeadQuartersTestingBackend:
    if settings.IS_PROD or settings.IS_STAGING:
        return EntrepriseWithHeadQuartersBackend()
    return EntrepriseWithHeadQuartersTestingBackend()


def venues_from_offerers_with_one_unique_virtual_venue() -> BaseQuery:
    ids = {row[0] for row in db.session.execute(QUERY)}
    return Venue.query.filter(Venue.id.in_(ids)).options(sa_orm.joinedload(Venue.managingOfferer))


def get_siret(venue: Venue) -> SiretInfo:
    """Find a venue's siret using its managing offerer's head quarters"""
    if not venue.managingOfferer.siren:
        raise MissingSirenError(f"venue #{venue.id}")

    siren = venue.managingOfferer.siren[:9]
    try:
        siret_info = get_backend().get_head_quarter(siren)
    except Exception as err:
        raise FetchSiretError(f"venue #{venue.id} / siren: #{siren}") from err

    return siret_info


def get_address(venue: Venue, siret_info: SiretInfo) -> Address:
    """Search address based on siret_info's geographical data.

    If nothing is found, use the BAN API and create the missing address.
    """
    addresses = search_addresses(
        street=siret_info.address.street, city=siret_info.address.city, postal_code=siret_info.address.postal_code
    )

    if addresses:
        return addresses[0]

    ban_address = _get_ban_address_or_none(
        street=siret_info.address.street, postal_code=siret_info.address.postal_code, city=siret_info.address.city
    )

    if ban_address:
        location_data = LocationData(
            street=ban_address.street,
            city=ban_address.city,
            postal_code=ban_address.postcode,
            insee_code=ban_address.citycode,
            latitude=ban_address.latitude,
            longitude=ban_address.longitude,
            ban_id=ban_address.id,
        )
    else:
        msg = (
            f"venue #{venue.id} / "
            f"street: '#{siret_info.address.street}' / "
            f"city: '#{siret_info.address.city}' / "
            f"postal code: '#{siret_info.address.postal_code}'"
        )
        raise FetchAddressError(msg)

    return get_or_create_address(
        location_data=location_data,
        is_manual_edition=True,
    )


def transform_virtual_venue(venue: Venue) -> None:
    if not venue.isVirtual:
        raise NotAVirtualVenue(f"venue #{venue.id}")

    siret_info = get_siret(venue)
    address = get_address(venue, siret_info)
    offerer_address = get_or_create_offerer_address(offerer_id=venue.managingOffererId, address_id=address.id)

    venue.siret = siret_info.siret

    venue.isVirtual = False
    venue.venueTypeCode = VenueTypeCode.ADMINISTRATIVE

    venue.street = address.street  # type: ignore[method-assign]
    venue.departementCode = address.departmentCode
    venue.postalCode = address.postalCode
    venue.city = address.city
    venue.latitude = address.latitude
    venue.longitude = address.longitude
    venue.offererAddress = offerer_address

    db.session.flush()


def transform_venues_from_offerers_with_one_unique_virtual_venue() -> Collection[int]:
    def transform_commit_and_log(venue: Venue) -> int | None:
        logger.info("start venue transformation... %s", venue.id)

        try:
            with transaction():
                transform_virtual_venue(venue)
        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.info("venue transformation for %s failed because of: %s", venue.id, err)
            return None

        logger.info("venue transformation for %s done!", venue.id)
        return venue.id

    venues = venues_from_offerers_with_one_unique_virtual_venue()
    ids = [transform_commit_and_log(venue) for venue in venues]
    return {_id for _id in ids if _id}


if __name__ == "__main__":
    transform_venues_from_offerers_with_one_unique_virtual_venue()
