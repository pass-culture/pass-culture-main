"""A client for "API Entreprise": https://entreprise.api.gouv.fr/

Documentation: https://entreprise.api.gouv.fr/developpeurs/
Staging data: https://github.com/etalab/siade_staging_data

For security reasons, non-public data should not be stored in pass Culture database.
Data is not persistent on the platform after redis cache expiration.
"""

import datetime
import json
import logging
import random
import re
import time
import typing
from urllib.parse import urljoin

from flask import current_app

from pcapi import settings
from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import models
from pcapi.connectors.entreprise.backends.base import BaseBackend
from pcapi.core import logging as pcapi_logging
from pcapi.utils import cache as cache_utils
from pcapi.utils import date as date_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)

CACHE_DURATION = datetime.timedelta(hours=6)
PASS_CULTURE_CONTEXT = "Vérification des acteurs culturels inscrits sur le pass Culture"


class EntrepriseBackend(BaseBackend):
    # less than 1-minute nginx timeout
    timeout = 50

    @staticmethod
    def _get_lock_name(subpath: str) -> str:
        # result is "/v3/insee/", "/v4/dgfip/", etc. which keeps rate limit by provider
        return f"cache:entreprise:{subpath[:-len(subpath.split('/', 3)[3])]}:lock"

    def _check_rate_limit(self, subpath: str, headers: typing.Mapping[str, str]) -> None:
        """
        Documentation: https://entreprise.api.gouv.fr/developpeurs#respecter-la-volumétrie
        Be careful with DGFIP endpoint: rate limit is 5 calls per minute!
        """
        rate_limit_total = headers.get("RateLimit-Limit")
        if not rate_limit_total:
            return

        rate_limit_remaining = headers.get("RateLimit-Remaining")
        rate_limit_reset = headers.get("RateLimit-Reset")

        assert rate_limit_remaining  # helps mypy
        assert rate_limit_reset  # helps mypy

        percent_reached = 100 - (100 * int(rate_limit_remaining)) / int(rate_limit_total)
        seconds_before_reset = int(rate_limit_reset) - int(time.time())
        if percent_reached > 80:
            logger.warning(
                "More than 80% of rate limit reached on API Entreprise",
                extra={
                    "subpath": subpath,
                    "percent": percent_reached,
                    "limit": int(rate_limit_total),
                    "remaining": int(rate_limit_remaining),
                    "seconds_before_reset": seconds_before_reset,
                },
            )
            current_app.redis_client.set(self._get_lock_name(subpath), "1", ex=max(1, seconds_before_reset))

    def _ensure_rate_limit(self, subpath: str) -> None:
        """
        Ensure that we don't reach rate limit for the requested endpoint.
        Rather, wait until reset time when reasonable.
        """
        slept_time = 0.0
        while (ttl := current_app.redis_client.ttl(self._get_lock_name(subpath))) > 0:
            if slept_time + ttl > self.timeout:
                raise exceptions.RateLimitExceeded("Rate limited, please try again later")
            # Some randomness (+ 0 to 2 seconds) so that concurrent calls do not start at the same time
            time_to_sleep = ttl + random.random() * 2
            time.sleep(time_to_sleep)
            slept_time += time_to_sleep

    def _check_siren_can_be_requested(self, siren: str) -> None:
        # Pass Culture also acts as an offerer which organizes events.
        # Avoid HTTP 422 Unprocessable Content "Le paramètre recipient est identique au SIRET/SIREN appelé."
        if siren == settings.PASS_CULTURE_SIRET[:9]:
            raise exceptions.EntrepriseException("Pass Culture")

    def _get(self, subpath: str) -> dict:
        if not settings.ENTREPRISE_API_URL:
            raise ValueError("ENTREPRISE_API_URL is not configured")

        url = urljoin(settings.ENTREPRISE_API_URL, subpath)

        # Mandatory parameters for traceability
        # See: https://entreprise.api.gouv.fr/developpeurs#renseigner-les-paramètres-dappel-et-de-traçabilité
        params = {
            "recipient": settings.PASS_CULTURE_SIRET,
            "context": PASS_CULTURE_CONTEXT,
            # trace id helps to identify context and user in GCP logs, less than 50 characters
            "object": f"{settings.ENV},{pcapi_logging.get_or_set_correlation_id()}",
        }

        headers = {"Authorization": "Bearer " + settings.ENTREPRISE_API_TOKEN}

        self._ensure_rate_limit(subpath)

        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            logger.exception("Network error on API Entreprise", extra={"exc": exc, "url": url})
            raise exceptions.ApiException(f"Network error on API Entreprise: {url}") from exc

        self._check_rate_limit(subpath, response.headers)

        if not response.ok:
            try:
                errors = response.json()["errors"]
                try:
                    # By default, the most specific error from the provider
                    error_message = errors[0]["meta"]["provider_errors"][0]["description"]
                except (ValueError, KeyError):
                    # If not, fallback to the generic error (common label for all APIs)
                    error_message = errors[0]["detail"]
                except TypeError:
                    error_message = errors[0]
            except json.JSONDecodeError:
                errors = None
                error_message = None

            if response.status_code == 404:
                raise exceptions.UnknownEntityException(error_message)
            if response.status_code == 429:
                logger.error("Rate Limit exceeded to API Entreprise", extra={"errors": errors})
                raise exceptions.RateLimitExceeded(error_message)
            if response.status_code == 451:
                raise exceptions.NonPublicDataException(error_message)
            if response.status_code in (500, 502, 503, 504):
                raise exceptions.ApiUnavailable(error_message)

            if errors:
                # 400, 401, 403, 422 are about wrong syntax or configuration, should be reported in Sentry
                # See: https://entreprise.api.gouv.fr/developpeurs#g%C3%A9rer-les-erreurs---codes-https
                logger.error(
                    "Error when calling API Entreprise",
                    extra={"url": url, "status_code": response.status_code, "errors": errors},
                )
            if not error_message:
                error_message = f"Error {response.status_code} from API Entreprise: {url}"
            raise exceptions.ApiException(error_message)
        try:
            return response.json()
        except json.JSONDecodeError:
            raise exceptions.ApiException(f"Unexpected non-JSON response from Sirene API: {url}")

    def _cached_get(self, subpath: str) -> dict:
        key_template = f"cache:entreprise:{subpath}"
        cached = cache_utils.get_from_cache(
            retriever=lambda: json.dumps(self._get(subpath)),
            key_template=key_template,
            expire=CACHE_DURATION.seconds,
        )
        assert isinstance(cached, str)  # help mypy
        return json.loads(cached)

    def _is_diffusible(self, data: dict) -> bool:
        return data["diffusable_commercialement"] is True and data["status_diffusion"] == "diffusible"

    def _get_name_from_sirene_data(self, data: dict) -> str:
        if data["type"] == "personne_physique":
            attrs = data["personne_physique_attributs"]
            name = " ".join(
                filter(
                    bool,
                    (
                        attrs["prenom_usuel"],
                        attrs["nom_naissance"],
                        attrs["nom_usage"],
                    ),
                )
            )
        else:  # "personne_morale"
            name = data["personne_morale_attributs"]["raison_sociale"]
        assert name
        return name

    def _get_address_from_sirene_data(self, data: dict) -> models.SireneAddress:
        # Every field is in the response but may be null, for example
        # for foreign addresses, which we don't support.
        # The API includes the arrondissement (e.g. "PARIS 1"), remove it.
        city = re.sub(r" \d+ *$", "", data["libelle_commune"] or "")
        return models.SireneAddress(
            street=" ".join(
                filter(
                    bool,
                    (
                        data["complement_adresse"],
                        data["numero_voie"],
                        data["indice_repetition_voie"],
                        data["type_voie"],
                        data["libelle_voie"],
                    ),
                )
            ),
            postal_code=data["code_postal"] or "",
            city=city,
            insee_code=data["code_commune"] or "",
        )

    def get_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/catalogue/insee/unites_legales
                       https://entreprise.api.gouv.fr/catalogue/insee/siege_social
        """
        self._check_siren_can_be_requested(siren)
        subpath = f"/v3/insee/sirene/unites_legales/{siren}"
        if with_address:
            # Also get head office SIRET data to avoid a second API call to get address
            subpath += "/siege_social"
        data = self._cached_get(subpath)["data"]
        siren_data = data["unite_legale"] if with_address else data

        is_diffusible = self._is_diffusible(siren_data)
        if raise_if_non_public and not is_diffusible:
            raise exceptions.NonPublicDataException()

        head_office_siret = siren_data["siret_siege_social"]
        address = self._get_address_from_sirene_data(data["adresse"]) if with_address else None

        return models.SirenInfo(
            siren=siren_data["siren"],
            name=self._get_name_from_sirene_data(siren_data),
            head_office_siret=head_office_siret,
            ape_code=siren_data["activite_principale"]["code"],
            ape_label=data["activite_principale"]["libelle"],
            active=siren_data["etat_administratif"] == "A",
            diffusible=is_diffusible,
            legal_category_code=siren_data["forme_juridique"]["code"],
            address=address,
            creation_date=date_utils.utc_datetime_to_department_timezone(
                # API Entreprise dates are timestamped at 0:00 Metropolitan French time
                datetime.datetime.fromtimestamp(siren_data["date_creation"]),
                departement_code=None,
            ).date(),
        )

    def get_siret(self, siret: str, raise_if_non_public: bool = False) -> models.SiretInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/catalogue/insee/etablissements
        """
        self._check_siren_can_be_requested(siret[:9])
        subpath = f"/v3/insee/sirene/etablissements/{siret}"
        data = self._cached_get(subpath)["data"]

        is_diffusible = self._is_diffusible(data)
        if raise_if_non_public and not is_diffusible:
            raise exceptions.NonPublicDataException()

        return models.SiretInfo(
            siret=siret,
            active=data["etat_administratif"] == "A",
            diffusible=is_diffusible,
            name=self._get_name_from_sirene_data(data["unite_legale"]),
            address=self._get_address_from_sirene_data(data["adresse"]),
            ape_code=data["activite_principale"]["code"],
            ape_label=data["activite_principale"]["libelle"],
            legal_category_code=data["unite_legale"]["forme_juridique"]["code"],
        )

    def get_rcs(self, siren: str) -> models.RCSInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/catalogue/infogreffe/rcs/extrait
        """
        self._check_siren_can_be_requested(siren)
        subpath = f"/v3/infogreffe/rcs/unites_legales/{siren}/extrait_kbis"
        try:
            data = self._cached_get(subpath)["data"]
        except exceptions.UnknownEntityException:
            return models.RCSInfo(registered=False)

        return models.RCSInfo(
            registered=True,
            registration_date=data["date_immatriculation"],
            deregistration_date=data["date_radiation"],
            head_office_activity=data["etablissement_principal"]["activite"],
            corporate_officers=[
                models.RCSCorporateOfficer(
                    name=" ".join(filter(bool, (item.get("prenom"), item.get("nom"), item.get("raison_sociale")))),
                    role=item["fonction"],
                )
                for item in data["mandataires_sociaux"]
            ],
            observations=[
                models.RCSObservation(date=item["date"], label=item["libelle"]) for item in data["observations"]
            ],
        )

    def get_urssaf(self, siren: str) -> models.UrssafInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/catalogue/urssaf/attestation_vigilance
        """
        self._check_siren_can_be_requested(siren)
        subpath = f"/v4/urssaf/unites_legales/{siren}/attestation_vigilance"
        data = self._cached_get(subpath)["data"]
        return models.UrssafInfo(
            attestation_delivered=data["entity_status"]["code"] == "ok",  # always "ok" or "refus_de_delivrance"
            details=data["entity_status"]["description"],
            validity_start_date=data["date_debut_validite"],
            validity_end_date=data["date_fin_validite"],
            verification_code=data["code_securite"],
        )

    def get_dgfip(self, siren: str) -> models.DgfipInfo:
        """
        Documentation: https://entreprise.api.gouv.fr/catalogue/dgfip/attestations_fiscales
        """
        self._check_siren_can_be_requested(siren)
        subpath = f"/v4/dgfip/unites_legales/{siren}/attestation_fiscale"
        data = self._cached_get(subpath)["data"]
        return models.DgfipInfo(
            attestation_delivered=bool(data["document_url"]),
            attestation_date=data["date_delivrance_attestation"],
            verified_date=data["date_periode_analysee"],
        )
