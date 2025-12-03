"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=pc-38958-script-create-venue-for-old-validated-offerers \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=create_venue_for_old_offerers \
  -f SCRIPT_ARGUMENTS="";

This script creates a Venue for an Offerer created a long time ago which is still validated/active and does not have a
Venue. Such an offerer has not created any offer in the past years but now comes back and can't login because of
frontend which does no longer deal with offerers without venue.
Try to fix when possible, without too much effort on corner cases because many of them will never try to connect again.
One by one, when requested by support team.
"""

import argparse
import datetime
import json
import logging
import re
import typing

from sqlalchemy.exc import IntegrityError

from pcapi import settings
from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import models
from pcapi.connectors.entreprise.backends.base import BaseBackend
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.models import db
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import cache as cache_utils
from pcapi.utils import requests
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

CACHE_DURATION = datetime.timedelta(minutes=15)


class InseeBackend(BaseBackend):
    """
    Former backend, better than API Entreprise because it works on staging with real data.
    Code retrieved from git history.
    """

    base_url = settings.INSEE_SIRENE_API_URL
    timeout = 3

    @property
    def headers(self) -> dict[str, str]:
        return {"X-INSEE-Api-Key-Integration": settings.INSEE_SIRENE_API_TOKEN}

    def _get(self, subpath: str) -> dict:
        url = self.base_url + subpath
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            logger.exception("Network error on Sirene API", extra={"exc": exc, "url": url})
            raise exceptions.ApiException(f"Network error on Sirene API: {url}") from exc
        if response.status_code == 400:
            raise exceptions.InvalidFormatException()
        if response.status_code == 403:
            raise exceptions.NonPublicDataException()
        if response.status_code in (301, 404):
            raise exceptions.UnknownEntityException()
        if response.status_code == 429:
            raise ValueError("Pass Culture exceeded Sirene API rate limit")
        if response.status_code in (500, 503):
            raise exceptions.ApiException("Sirene API is unavailable")
        if response.status_code != 200:
            raise exceptions.ApiException(f"Unexpected {response.status_code} response from Sirene API: {url}")
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise exceptions.ApiException(f"Unexpected non-JSON response from Sirene API: {url}")

    def _cached_get(self, subpath: str) -> dict:
        key_template = f"cache:sirene:{subpath}"
        cached = cache_utils.get_from_cache(
            retriever=lambda: json.dumps(self._get(subpath)),
            key_template=key_template,
            expire=CACHE_DURATION.seconds,
        )
        assert isinstance(cached, str)  # help mypy
        return json.loads(cached)

    def _check_non_public_data(self, info: models.SirenInfo | models.SiretInfo) -> None:
        # If the data is not public (which is known as "non diffusibles"
        # in Insee jargon), some fields are populated with "[ND]".
        #
        # There is also a "statutDiffusionUniteLegale" field in the
        # response that says whether there is non-public data. But
        # perhaps the data we want is public, and the non-public data
        # is something we're not interested in. So it's probably
        # better to look only at the data we use. (Obviously, this
        # will fail badly if a company is named "[ND]". We'll suppose
        # it's unlikely.)
        def _check_values(values: typing.Iterable) -> None:
            for value in values:
                if isinstance(value, dict):
                    _check_values(value.values())
                elif value == "[ND]":
                    raise exceptions.NonPublicDataException()

        _check_values(info.dict().values())

    def _get_head_office(self, siren_data: dict) -> dict:
        today = datetime.date.today().isoformat()
        for periode in siren_data["periodesUniteLegale"]:
            if (not periode["dateDebut"] or periode["dateDebut"] <= today) and (
                not periode["dateFin"] or periode["dateFin"] >= today
            ):
                return periode
        # In case all "periodes" are in the future (or the single period: "dateCreationUniteLegale" in the future):
        # Note that the company will be considered as active even before "dateCreationUniteLegale".
        return [_b for _b in siren_data["periodesUniteLegale"] if not _b["dateFin"]][0]

    def _get_name_from_siren_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siret_data()` below.
        head_office = self._get_head_office(data)
        # Company
        if head_office.get("denominationUniteLegale"):
            return head_office["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((data["prenom1UniteLegale"], head_office["nomUniteLegale"]))

    def _get_closure_date_from_siren_data(self, siren_data: dict) -> datetime.date | None:
        # Several "periodesUniteLegale" can be closed.
        # This method may return a date in the future, when active is still True.
        closure_date = None
        sorted_periodes = sorted(
            siren_data["periodesUniteLegale"], key=lambda periode: periode["dateDebut"], reverse=True
        )
        for periode in sorted_periodes:
            if periode["etatAdministratifUniteLegale"] != "C":
                break
            closure_date = periode["dateDebut"]
        return datetime.date.fromisoformat(closure_date) if closure_date else None

    def _get_name_from_siret_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siren_data()` above.
        block = data["uniteLegale"]
        # Company
        if block.get("denominationUniteLegale"):
            return block["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((block["prenom1UniteLegale"], block["nomUniteLegale"]))

    def _get_address_from_siret_data(self, data: dict) -> models.SireneAddress:
        block = data["adresseEtablissement"]
        # Every field is in the response but may be null, for example
        # for foreign addresses, which we don't support.
        # The API includes the arrondissement (e.g. "PARIS 1"), remove it.
        city = re.sub(r" \d+ *$", "", block["libelleCommuneEtablissement"] or "")
        # Until Sirene API return postalCode of Saint-Martin
        # we need to do this hacky thing, otherwise Saint-Martin
        # users won't be able to create offerers.
        postal_code = block["codePostalEtablissement"] or ""
        if not postal_code and block["codeCommuneEtablissement"] == "97801":
            postal_code = "97150"

        return models.SireneAddress(
            street=" ".join(
                (
                    block["numeroVoieEtablissement"] or "",
                    block["typeVoieEtablissement"] or "",
                    block["libelleVoieEtablissement"] or "",
                )
            ).strip(),
            postal_code=postal_code,
            city=city,
            insee_code=block["codeCommuneEtablissement"] or "",
        )

    def _format_ape_code(self, ape_code: str | None) -> str | None:
        if not ape_code:
            return None
        return ape_code.replace(".", "")

    def get_siren_open_data(
        self, siren: str, with_address: bool = True, raise_if_non_public: bool = True
    ) -> models.SirenInfo:
        subpath = f"/siren/{siren}"
        data = self._cached_get(subpath)["uniteLegale"]
        head_office = self._get_head_office(data)
        head_office_siret = siren + head_office["nicSiegeUniteLegale"]
        address = (
            self.get_siret(head_office_siret, raise_if_non_public=raise_if_non_public).address if with_address else None
        )
        info = models.SirenInfo(
            siren=siren,
            name=self._get_name_from_siren_data(data),
            head_office_siret=head_office_siret,
            legal_category_code=head_office["categorieJuridiqueUniteLegale"],
            ape_code=self._format_ape_code(head_office.get("activitePrincipaleUniteLegale")),
            address=address,
            active=head_office["etatAdministratifUniteLegale"] == "A",
            diffusible=data["statutDiffusionUniteLegale"] == "O",
            creation_date=datetime.date.fromisoformat(data["dateCreationUniteLegale"]),
            closure_date=self._get_closure_date_from_siren_data(data),
        )
        if raise_if_non_public:
            self._check_non_public_data(info)
        return info

    def get_siret_open_data(self, siret: str, raise_if_non_public: bool = True) -> models.SiretInfo:
        subpath = f"/siret/{siret}"
        data = self._cached_get(subpath)["etablissement"]
        legal_unit_block = data["uniteLegale"]
        try:
            block = [_b for _b in data["periodesEtablissement"] if _b["dateFin"] is None][0]
            active = block["etatAdministratifEtablissement"] == "A"
        except IndexError:
            active = False
        info = models.SiretInfo(
            siret=siret,
            siren=siret[:9],
            active=active,
            diffusible=legal_unit_block["statutDiffusionUniteLegale"] == "O",
            name=self._get_name_from_siret_data(data),
            address=self._get_address_from_siret_data(data),
            ape_code=self._format_ape_code(legal_unit_block.get("activitePrincipaleUniteLegale")),
            legal_category_code=legal_unit_block["categorieJuridiqueUniteLegale"],
        )
        if raise_if_non_public:
            self._check_non_public_data(info)
        return info


@atomic()
def _create_venue(offerer: offerers_models.Offerer) -> None:
    logger.info("Processing offerer %d, SIREN %s", offerer.id, offerer.siren)

    siren_info = InseeBackend().get_siren_open_data(offerer.siren, with_address=False, raise_if_non_public=False)
    siret_info = InseeBackend().get_siret_open_data(siren_info.head_office_siret, raise_if_non_public=False)

    if not siret_info.active:
        logger.info("SIRET %s is not active, skip", siret_info.siret)
        return

    logger.info(
        "Found SIRET %s in %s %s (%s)",
        siret_info.siret,
        siret_info.address.postal_code,
        siret_info.address.city,
        siret_info.address.insee_code,
    )

    address_data = None
    if siret_info.diffusible:
        try:
            address_info = api_adresse.get_address(
                address=siret_info.address.street,
                postcode=siret_info.address.postal_code,
                city=siret_info.address.city,
                citycode=siret_info.address.insee_code,
                strict=True,
            )
            address_data = offerers_schemas.AddressBodyModel(
                isVenueAddress=True,
                isManualEdition=False,
                banId=address_info.id,
                city=offerers_schemas.VenueCity(address_info.city),
                inseeCode=offerers_schemas.VenueInseeCode(address_info.citycode),
                label=None,
                latitude=address_info.latitude,
                longitude=address_info.longitude,
                postalCode=offerers_schemas.VenuePostalCode(address_info.postcode),
                street=offerers_schemas.VenueAddress(address_info.street),
            )
        except api_adresse.AdresseException:  # No result, unexpected input, server error...
            pass

    if not address_data:
        try:
            municipality_info = api_adresse.get_municipality_centroid(
                citycode=siret_info.address.insee_code, city=siret_info.address.city
            )
            latitude = municipality_info.latitude
            longitude = municipality_info.longitude
            postal_code = municipality_info.postcode
        except api_adresse.AdresseException:  # No result, unexpected input, server error...
            # Coordinates are mandatory, fallback in the ocean.
            # Data is not consistent but we can't do better, this script is for old offerers without venues so that
            # pro accounts can still login when they come back; pro can modify later when he connects to PC PRO.
            latitude = 0
            longitude = 0
            postal_code = siret_info.address.postal_code if siret_info.diffusible else offerer.postalCode  # type: ignore[assignment]

        address_data = offerers_schemas.AddressBodyModel(
            isVenueAddress=True,
            isManualEdition=True,
            banId=None,
            city=offerers_schemas.VenueCity(siret_info.address.city),
            inseeCode=offerers_schemas.VenueInseeCode(siret_info.address.insee_code),
            label=None,
            latitude=latitude,
            longitude=longitude,
            postalCode=offerers_schemas.VenuePostalCode(postal_code),
            street=offerers_schemas.VenueAddress(siret_info.address.street or "n/a"),
        )

    venue_creation_info = venues_serialize.PostVenueBodyModel(
        activity=offerers_models.Activity.NOT_ASSIGNED,
        address=address_data,
        bookingEmail=offerers_schemas.VenueBookingEmail(""),
        comment=None,
        managingOffererId=offerer.id,
        name=offerers_schemas.VenueName(siret_info.name if siret_info.diffusible else offerer.name),
        publicName=offerers_schemas.VenuePublicName(siret_info.name if siret_info.diffusible else offerer.name),
        siret=offerers_schemas.VenueSiret(siret_info.siret),
        venueLabelId=None,
        venueTypeCode=offerers_models.VenueTypeCode.OTHER.name,
        withdrawalDetails=None,
        description=None,
        contact=None,
        audioDisabilityCompliant=False,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=False,
        isOpenToPublic=False,
    )
    venue = offerers_api.create_venue(venue_creation_info, author=None)  # type: ignore[arg-type]

    logging.info("Created venue %s", venue.id)


@atomic()
def main(offerer_id: int, is_dry_run: bool) -> None:
    if is_dry_run:
        mark_transaction_as_invalid()

    offerer = (
        db.session.query(offerers_models.Offerer)
        .outerjoin(offerers_models.Venue)
        .filter(
            offerers_models.Offerer.id == offerer_id,
            offerers_models.Offerer.isActive.is_(True),
            offerers_models.Offerer.isValidated,
            offerers_models.Venue.id.is_(None),
        )
        .one_or_none()
    )

    if not offerer:
        logger.warning("Offerer %d not found or does not meet requirements", offerer_id)
        mark_transaction_as_invalid()
        return

    try:
        _create_venue(offerer)
    except IntegrityError as exc:
        # Don't try to deal with exceptions (SIRET which exists somewhere else...), pro may never try to connect
        logger.exception("Failed to create venue. %s", exc)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--offerer-id", type=int, required=True)
    args = parser.parse_args()

    main(args.offerer_id, not args.not_dry)
