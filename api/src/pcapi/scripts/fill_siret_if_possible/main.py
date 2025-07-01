"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36268-api-attribuer-un-siret-a-des-venues-sur-des-offerer-sans-siret/api/src/pcapi/scripts/fill_siret_if_possible/main.py

"""

import argparse
import logging
import typing

import sqlalchemy.orm as sa_orm

import pcapi.connectors.entreprise.backends.api_entreprise as entreprise_backend
import pcapi.connectors.entreprise.exceptions as entreprise_exceptions
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.schemas as offerers_schemas
import pcapi.models.validation_status_mixin as validation_status_models
from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


class ExtendedEntrepriseBackend(entreprise_backend.EntrepriseBackend):
    def get_siret_from_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> str:
        self._check_siren_can_be_requested(siren)
        subpath = f"/v3/insee/sirene/unites_legales/{siren}"
        if with_address:
            # Also get head office SIRET data to avoid a second API call to get address
            subpath += "/siege_social"
        data = self._cached_get(subpath)["data"]
        siren_data = data["unite_legale"] if with_address else data

        is_diffusible = self._is_diffusible(siren_data)
        if raise_if_non_public and not is_diffusible:
            raise entreprise_exceptions.NonPublicDataException()

        return siren_data["siret_siege_social"]


def get_offerers_without_siret() -> list[offerers_models.Offerer]:
    offerer_ids_with_siret = (
        offerers_models.Offerer.query.join(offerers_models.Offerer.managedVenues)
        .filter(
            offerers_models.Venue.siret.is_not(None),
        )
        .with_entities(offerers_models.Offerer.id)
    )
    return (
        offerers_models.Offerer.query.join(offerers_models.Offerer.managedVenues)
        .filter(
            offerers_models.Venue.siret.is_(None),
            offerers_models.Venue.isVirtual == False,
            offerers_models.Offerer.validationStatus != validation_status_models.ValidationStatus.CLOSED,
            offerers_models.Offerer.id.not_in(offerer_ids_with_siret),
        )
        .options(
            sa_orm.contains_eager(offerers_models.Offerer.managedVenues),
        )
        .order_by(offerers_models.Offerer.id)
        .all()
    )


@atomic()
def main(not_dry: bool) -> None:
    enterprise_backend = ExtendedEntrepriseBackend()
    offerers = get_offerers_without_siret()
    for offerer in offerers:
        if not offerer.siren:
            logger.warning(f"Offerer {offerer.id} has no SIREN, cannot fill SIRET for its venues. Skipping.")
            continue
        venues = sorted([venue for venue in offerer.managedVenues if not venue.isVirtual], key=lambda v: v.id)
        if not venues:
            logger.warning(f"Offerer {offerer.id} has no physical venues, cannot fill SIRET. Skipping.")
            continue
        venue = venues[0]
        siret = enterprise_backend.get_siret_from_siren(offerer.siren, raise_if_non_public=True)
        siret_data = enterprise_backend.get_siret(siret)
        venue.siret = siret
        venue.name = siret_data.name
        city_info = api_adresse.get_municipality_centroid(
            siret_data.address.city, postcode=siret_data.address.postal_code, citycode=siret_data.address.insee_code
        )
        address = offerers_schemas.AddressBodyModel(
            isManualEdition=True,
            isVenueAddress=True,
            label=None,
            banId=None,
            street=typing.cast(offerers_schemas.VenueAddress, siret_data.address.street),
            postalCode=typing.cast(offerers_schemas.VenuePostalCode, siret_data.address.postal_code),
            city=typing.cast(offerers_schemas.VenueCity, siret_data.address.city),
            inseeCode=typing.cast(offerers_schemas.VenueInseeCode, siret_data.address.insee_code),
            latitude=city_info.latitude,
            longitude=city_info.longitude,
        )
        offerer_address = offerers_api.get_offerer_address_from_address(offerer.id, address)
        venue.offererAddress = offerer_address
        db.session.add(venue)

    if not not_dry:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
