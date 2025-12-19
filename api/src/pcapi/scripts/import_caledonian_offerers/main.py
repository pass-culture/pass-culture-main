"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=production \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=import_caledonian_offerers \
  -f SCRIPT_ARGUMENTS="";

Script which imports Caledonian offerers and venues from a CSV file.
"""

import argparse
import csv
import functools
import logging
import os
from decimal import Decimal
from functools import partial

from pydantic import BaseModel

import pcapi.utils.email as email_utils
from pcapi.app import app
from pcapi.core import search
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import regions as regions_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


class ImportCounters(BaseModel):
    already_existing_venues: int = 0
    already_existing_offerers: int = 0


NEW_CALEDONIA_TIMEZONE = "Pacific/Noumea"


def is_eligible_postal_code(postal_code: str) -> bool:
    return postal_code.startswith(regions_utils.NEW_CALEDONIA_DEPARTMENT_CODE)


CSV_COLUMN_MAPPING = {
    "ridet": "RIDET",
    "public_name": "Nom de la structure",
    "venue_name": "Raison sociale",
    "offerer_name": "Nom de l'entité juridique",
    "street": "voie de la structure",
    "postal_code": "Code postal",
    "city": "Ville",
    "latitude": "latitude (5 chiffres)",
    "longitude": "longitude",
    "activity": "Activité principale",
    "visual_access": "Visuel",
    "cognitive_access": "Cognitif",
    "motor_access": "Moteur",
    "auditory_access": "Auditif",
    "not_accessible": "Non accessible",
    "booking_email": "Adresse mail",
}

MANDATORY_FIELDS = {"ridet", "venue_name", "postal_code", "city", "street", "address", "latitude", "longitude"}


def parse_csv_data(rows: list[dict]) -> list[dict]:
    data_rows = []

    for i, row in enumerate(rows):
        ridet = row[CSV_COLUMN_MAPPING["ridet"]].strip().replace(" ", "").replace(".", "")

        if not ridet:
            logger.warn(f"Ridet is missing for row line {i}")
            continue

        extracted_data = {}
        for field, csv_column in CSV_COLUMN_MAPPING.items():
            value = row[csv_column].strip()
            has_missing_data = False
            if field in MANDATORY_FIELDS and not value:
                logger.error(f"Données incomplètes pour la ligne {i}. Il manque le champ {field}")
                has_missing_data = True

            if has_missing_data:
                continue

            if field in ["visual_access", "cognitive_access", "motor_access", "auditory_access", "not_accessible"]:
                extracted_data[field] = value.lower() == "true"
            elif field in ["latitude", "longitude"]:
                extracted_data[field] = Decimal(value)
            else:
                extracted_data[field] = value.strip()

        # Mapping du type de venue
        activity = str(extracted_data["activity"])

        try:
            venue_type_code = offerers_models.VenueTypeCode(activity)
        except ValueError as e:
            logger.warning(f"Erreur lors du mapping du type de venue: {e}")
            venue_type_code = offerers_models.VenueTypeCode.OTHER

        extracted_data["venue_type_code"] = venue_type_code

        extracted_data["address"] = extracted_data["street"]

        data_rows.append(extracted_data)

    return data_rows


def create_or_get_address(address_data: dict) -> geography_models.Address:
    street = address_data["address"]
    postal_code = address_data["postal_code"]
    city = address_data["city"]
    latitude = address_data["latitude"]
    longitude = address_data["longitude"]

    # Vérifier que le code postal est neo calédonien
    if postal_code and not is_eligible_postal_code(postal_code):
        raise ValueError(f"Code postal non éligible: {postal_code}")

    # Chercher si l'adresse existe déjà
    existing_address = (
        db.session.query(geography_models.Address)
        .filter(
            geography_models.Address.street == street,
            geography_models.Address.postalCode == postal_code,
            geography_models.Address.city == city,
        )
        .one_or_none()
    )

    if existing_address:
        return existing_address

    # Créer une nouvelle adresse
    address = geography_models.Address(
        street=street,
        postalCode=postal_code,
        city=city,
        latitude=latitude,
        longitude=longitude,
        departmentCode=regions_utils.NEW_CALEDONIA_DEPARTMENT_CODE,
        timezone=NEW_CALEDONIA_TIMEZONE,
        isManualEdition=True,
    )

    db.session.add(address)
    db.session.flush()

    return address


def create_offerer_and_venue(data: dict, counters: ImportCounters, comment: str) -> offerers_models.Offerer:
    logging.info("Processing RIDET %s", data["ridet"])

    """Crée un offerer et sa venue correspondante."""
    ridet = data["ridet"].strip().replace(" ", "").replace(".", "")
    venue_name = data["venue_name"]
    offerer_name = data["offerer_name"]

    rid7 = ridet[:7]
    siren = siren_utils.rid7_to_siren(rid7)

    existing_offerer = (
        db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren == siren).one_or_none()
    )

    if existing_offerer:
        logger.info(f"Offerer existant trouvé: {existing_offerer.name} (SIREN: {siren})")
        counters.already_existing_offerers += 1
        offerer = existing_offerer
    else:
        offerer = offerers_models.Offerer(
            name=offerer_name,
            siren=siren,
            isActive=True,
            validationStatus=ValidationStatus.VALIDATED,
            allowedOnAdage=False,
        )

        db.session.add(offerer)
        history_api.add_action(
            history_models.ActionType.OFFERER_VALIDATED,
            author=None,
            offerer=offerer,
            comment=f"Création des acteurs culturels calédoniens par script - {comment}",
        )
        offerers_api.update_fraud_info(
            offerer=offerer,
            author_user=None,
            confidence_level=offerers_models.OffererConfidenceLevel.MANUAL_REVIEW,
            comment="Revue manuelle de toutes les offres des acteurs calédoniens",
        )
        db.session.flush()
        logger.info(f"Offerer créé: {offerer.name} (SIREN: {siren})")

    existing_venue = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.siret == siren_utils.ridet_to_siret(ridet))
        .one_or_none()
    )

    if existing_venue:
        logger.info(f"Venue existante trouvée: {existing_venue.name} (SIRET: {existing_venue.siret})")
        counters.already_existing_venues += 1
    else:
        address = create_or_get_address(data)

        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.offererId == offerer.id,
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label.is_(None),
            )
            .one_or_none()
        )

        if not offerer_address:
            offerer_address = offerers_models.OffererAddress(
                offerer=offerer,
                address=address,
                label=None,
            )
            db.session.add(offerer_address)
            db.session.flush()

        db.session.flush()

        booking_email = data.get("booking_email")
        if booking_email and not email_utils.is_valid_email(booking_email):
            logger.error("Invalid email address: %s", booking_email)

        venue = offerers_models.Venue(
            name=venue_name,
            siret=siren_utils.ridet_to_siret(ridet),
            managingOffererId=offerer.id,
            publicName=data.get("public_name"),
            isVirtual=False,
            isPermanent=True,
            isOpenToPublic=True,
            venueTypeCode=data.get("venue_type_code", offerers_models.VenueTypeCode.OTHER),
            dmsToken=offerers_api.generate_dms_token(),
            audioDisabilityCompliant=data.get("auditory_access"),
            mentalDisabilityCompliant=data.get("cognitive_access"),
            motorDisabilityCompliant=data.get("motor_access"),
            visualDisabilityCompliant=data.get("visual_access"),
            offererAddressId=offerer_address.id,
            bookingEmail=booking_email,
        )

        db.session.add(venue)
        history_api.add_action(
            history_models.ActionType.VENUE_CREATED,
            author=None,
            venue=venue,
            comment=f"Création des acteurs culturels calédoniens par script - {comment}",
        )
        db.session.flush()
        logger.info(f"Venue créée: {venue.name} (SIRET: {venue.siret})")

        logger.info(f"Adresse offerer créée: {venue_name}")

        offerers_api.link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

        on_commit(
            functools.partial(search.async_index_venue_ids, [venue.id], reason=search.IndexationReason.VENUE_CREATION)
        )

        if venue.bookingEmail:
            booking_email = str(venue.bookingEmail)
            external_attributes_api.update_external_pro(booking_email)
        zendesk_sell.create_venue(venue)

    return offerer


@atomic()
def main(filename: str, not_dry: bool) -> None:
    """Fonction principale d'import."""

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = f"{namespace_dir}/{filename}"
    logger.info(f"Mode dry run: {not not_dry}")
    logger.info(f"Processing file: {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"Fichier non trouvé: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = list(reader)
        data_rows = parse_csv_data(rows)

    if not data_rows:
        logger.warning("Aucune donnée trouvée dans le fichier CSV")
        return

    created_venues = 0
    counters = ImportCounters(
        already_existing_venues=0,
        already_existing_offerers=0,
    )
    errors = 0

    for idx, row in enumerate(data_rows):
        try:
            logger.info(f"Traitement de l'entrée {idx + 1}/{len(data_rows)}: {row['venue_name']}")

            offerer = create_offerer_and_venue(row, counters, comment=filename)

            on_commit(partial(update_zendesk_offerer, offerer.id))

            created_venues += 1

        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'entrée {idx + 1}: {e}")
            errors += 1
            continue

    if errors:
        raise Exception(f"Erreurs lors de l'import: {errors}")

    logger.info("Import terminé:")
    logger.info(f"- Venues créées: {created_venues}")
    logger.info(f"- Venues déjà existant: {counters.already_existing_venues}")
    logger.info(f"- Offerer déjà existant: {counters.already_existing_offerers}")
    logger.info(f"- Erreurs: {errors}")

    if not not_dry:
        mark_transaction_as_invalid()


def update_zendesk_offerer(offerer_id: int) -> None:
    offerer = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_id).one()
    logger.info(f"Updating Zendesk offerer: {offerer.id} (SIREN: {offerer.siren})")
    zendesk_sell.create_offerer(offerer)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--filename", type=str, required=True)
    args = parser.parse_args()

    main(filename=args.filename, not_dry=args.not_dry)
