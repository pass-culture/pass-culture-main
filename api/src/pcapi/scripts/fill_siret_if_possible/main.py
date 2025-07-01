"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36268-api-attribuer-un-siret-a-des-venues-sur-des-offerer-sans-siret/api/src/pcapi/scripts/fill_siret_if_possible/main.py

"""

import argparse
import csv
import logging
import os

import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm

import pcapi.connectors.entreprise.backends.api_entreprise as entreprise_backend
import pcapi.connectors.entreprise.exceptions as entreprise_exceptions
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.models.validation_status_mixin as validation_status_models
from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "Venue ID"


def _write_modifications(modifications: list[tuple[int, str]], filename: str) -> None:
    # csv output to check what has been done and what failed
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/{filename}"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Modification"])
        writer.writerows(modifications)


class ExtendedEntrepriseBackend(entreprise_backend.EntrepriseBackend):
    def get_siret_from_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> str:
        self._check_siren_can_be_requested(siren)
        subpath = f"/v3/insee/sirene/unites_legales/{siren}"
        if with_address:
            # Also get head office SIRET data to avoid a second API call to get address
            subpath += "/siege_social"
        data = self._get(subpath)["data"]
        siren_data = data["unite_legale"] if with_address else data

        is_diffusible = self._is_diffusible(siren_data)
        if raise_if_non_public and not is_diffusible:
            raise entreprise_exceptions.NonPublicDataException()

        return siren_data["siret_siege_social"]


class ExtendedApiAddressBackend(api_adresse.ApiAdresseBackend):
    def _get_address(
        self, street: str, postcode: str | None, citycode: str | None = None, city: str | None = None
    ) -> api_adresse.AddressInfo:
        params = {
            "q": self._remove_quotes(street),
            "postcode": postcode,
            "citycode": citycode,
            "city": self._remove_quotes(city),
            "autocomplete": 0,
            "limit": 1,
        }

        data = self._search(params=params)
        if self._is_result_empty(data):
            raise api_adresse.NoResultException

        result = self._format_result(data["features"][0])

        extra = {
            "id": result.id,
            "label": result.label,
            "latitude": result.latitude,
            "longitude": result.longitude,
            "queried_address": street,
            "score": result.score,
        }

        if result.score < api_adresse.RELIABLE_SCORE_THRESHOLD:
            logger.info("Result from API Adresse has a low score", extra=extra)
            raise api_adresse.NoResultException
        else:
            logger.info("Retrieved details from API Adresse for query", extra=extra)
        return result


def _get_offerers_without_siret() -> list[offerers_models.Offerer]:
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
def main(not_dry: bool, offerer_id: int | None = None) -> None:
    enterprise_backend = ExtendedEntrepriseBackend()
    api_adresse_backend = ExtendedApiAddressBackend()
    fails: list[tuple[int, str]] = []
    modifications: list[tuple[int, str]] = []

    if offerer_id:
        if offerer := db.session.query(offerers_models.Offerer).filter_by(id=offerer_id).one_or_none():
            offerers_list = [offerer]
        else:
            logger.warning(f"Offerer {offerer_id} not found. Exiting script")
            return
    else:
        offerers_list = _get_offerers_without_siret()

    for offerer in offerers_list:
        if not offerer.siren:
            logger.warning(f"Offerer {offerer.id} has no SIREN, cannot fill SIRET for its venues. Skipping.")
            continue

        venues: list[offerers_models.Venue] = sorted(
            [venue for venue in offerer.managedVenues if not venue.isVirtual], key=lambda v: v.id
        )
        if not venues:
            logger.warning(f"Offerer {offerer.id} has no physical venues, cannot fill SIRET. Skipping.")
            continue

        venue: offerers_models.Venue = venues[0]
        venue_id = venue.id

        try:
            siret = enterprise_backend.get_siret_from_siren(offerer.siren, raise_if_non_public=True)
        except entreprise_exceptions.ApiException:
            fails.append((venue_id, "Pas de SIRET trouvé pour cet offerer"))
            continue
        except entreprise_exceptions.NonPublicDataException:
            fails.append((venue_id, "SIRET non diffusible trouvé pour cet offerer"))
            continue
        except entreprise_exceptions.UnknownEntityException:
            fails.append((venue_id, "SIREN non trouvé dans l'API entreprise"))
            continue
        # 1. add siret
        try:
            siret_data = enterprise_backend.get_siret(siret)
        except entreprise_exceptions.ApiUnavailable:
            fails.append((venue_id, "Timeout de l'API entreprise, SIRET & Adresse non mis à jour"))
            continue
        except entreprise_exceptions.ApiException:
            fails.append((venue_id, "Problème lié à l'API entreprise, SIRET & Adresse non mis à jour"))
            continue
        venue.name = siret_data.name
        venue.siret = siret
        try:
            with atomic():
                db.session.add(venue)
                db.session.flush()
        except sa_exc.IntegrityError:
            fails.append((venue_id, "Siret already exists on this venue"))
            continue

        modifications.append(
            (
                venue_id,
                f"Ajout du SIRET {siret}",
            )
        )
        history_api.add_action(
            venue=venue,
            author=None,
            action_type=history_models.ActionType.VENUE_REGULARIZATION,
            comment="Siret ajouté à partir du SIREN, depuis l'API entreprise",
        )

        # 2. add address, if it fails, we will do it manually from failure log
        try:
            ban_address = api_adresse_backend._get_address(
                street=siret_data.address.street,
                postcode=siret_data.address.postal_code,
                city=siret_data.address.city,
                citycode=siret_data.address.insee_code,
            )
            log_address = f"{ban_address.street}, {ban_address.postcode}, {ban_address.city}"
            logger.info("Address for %s found in BAN :%s", offerer_id, log_address)
        except (api_adresse.NoResultException, api_adresse.InvalidFormatException):
            ban_address = None
            logger.info("No address found in BAN for %s", offerer_id)

        if ban_address:
            location_data = offerers_api.LocationData(
                city=ban_address.city,
                insee_code=ban_address.citycode,
                ban_id=ban_address.id,
                street=ban_address.street,
                postal_code=ban_address.postcode,
                latitude=ban_address.longitude,
                longitude=ban_address.latitude,
            )
        else:
            try:
                municipality_address = api_adresse.get_municipality_centroid(
                    city=siret_data.address.city, postcode=siret_data.address.postal_code
                )
            except api_adresse.InvalidFormatException:
                logger.info("API Address did not find any data for %s", offerer_id)
                fails.append(
                    (venue_id, "Pas de données trouvées pour cette venue sur l'API addresse (InvalidFormatException)")
                )
                continue
            except api_adresse.AdresseException:
                fails.append((venue_id, "Erreur (probablement un timeout sur l'API Adresse, adresse non mise à jour)"))
                continue
            location_data = offerers_api.LocationData(
                city=siret_data.address.city,
                insee_code=siret_data.address.insee_code,
                ban_id=None,
                street=siret_data.address.street,
                postal_code=siret_data.address.postal_code,
                longitude=municipality_address.longitude,
                latitude=municipality_address.latitude,
            )

        try:
            with atomic():
                address = offerers_api.get_or_create_address(location_data, is_manual_edition=(not ban_address))
                offerer_address = offerers_api.get_or_create_offerer_address(
                    offerer.id,
                    address.id,
                )
                venue.offererAddress = offerer_address
                db.session.add(venue)
                db.session.flush()
        except sa_exc.IntegrityError:
            fails.append((venue_id, "Something went wrong with OA. Address not changed"))
            continue

        log_address = (
            f"{offerer_address.address.street}, {offerer_address.address.city}, {offerer_address.address.postalCode}"
        )
        modifications.append(
            (
                venue_id,
                f"Ajout de la localisation {log_address}, OffererAddressId {offerer_address.id}",
            )
        )
        history_api.add_action(
            venue=venue,
            author=None,
            action_type=history_models.ActionType.VENUE_REGULARIZATION,
            comment="Adresse ajouté depuis l'API adresse",
        )
        logger.info("Adresse %s ajoutée à la venue %s", log_address, venue_id)

    _write_modifications(modifications=modifications, filename="add_siret.csv")
    _write_modifications(modifications=fails, filename="add_siret_fails.csv")

    if not not_dry:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--offerer-id", type=int, required=False)
    args = parser.parse_args()

    main(not_dry=args.not_dry, offerer_id=args.offerer_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
