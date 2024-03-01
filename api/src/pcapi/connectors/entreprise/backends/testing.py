from collections import defaultdict
import datetime

from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import models
from pcapi.connectors.entreprise.backends.base import BaseBackend


class TestingBackend(BaseBackend):
    address = models.SireneAddress(
        street="3 RUE DE VALOIS",
        postal_code="75001",
        city="PARIS",
        insee_code="75101",
    )

    nd_address = models.SireneAddress(
        street="[ND]",
        postal_code="[ND]",
        city="CANNES",
        insee_code="06029",
    )

    @classmethod
    def _check_siren(cls, siren: str) -> None:
        assert len(siren) == 9
        if siren == "000000000":
            raise exceptions.UnknownEntityException()

    @classmethod
    def _ape_code_and_label(cls, siren_or_siret: str) -> tuple[str, str]:
        # allows to get an offerer with a specific APE code using specific siren
        siren_ape = defaultdict(
            lambda: ("90.03A", "Création artistique relevant des arts plastiques"),
            {
                "777084112": ("84.11Z", "Administration publique générale"),
                "777084122": (
                    "84.12Z",
                    "Administration publique (tutelle) de la santé, de la formation, de la culture et des services sociaux, autre que sécurité sociale ",
                ),
                "777091032": (
                    "91.03Z",
                    "Gestion des sites et monuments historiques et des attractions touristiques similaires",
                ),
            },
        )

        return siren_ape[siren_or_siret[:9]]

    @classmethod
    def _legal_category_code(cls, siren_or_siret: str) -> str:
        # allows to get an offerer with a different legal category depending on siren
        match siren_or_siret[3]:
            case "5":
                return "5499"  # Société à responsabilité limitée (sans autre indication)
            case "6":
                return "5710"  # SAS, société par actions simplifiée
            case "7":
                return "7210"  # Commune et commune nouvelle
            case "8":
                return "7389"  # Établissement public national à caractère administratif
            case _:
                return "1000"  # Entreprise individuelle

    @classmethod
    def _is_active(cls, siren_or_siret: str) -> bool:
        # allows to get a closed offerer in dev/testing environments:
        # any SIREN which ends with "99" or SIRET in which SIREN part ends with "99"
        return siren_or_siret[7:9] != "99"

    @classmethod
    def _is_diffusible(cls, siren_or_siret: str) -> bool:
        # allows to get a non-diffusible offerer in dev/testing environments: any SIREN which starts with '9'
        return siren_or_siret[0] != "9"

    @classmethod
    def _is_commercial(cls, siren_or_siret: str) -> bool:
        # allows to get companies registered at the RCS or not, depending on the second digit in the SIREN/SIRET
        return int(siren_or_siret[1]) % 2 == 1

    @classmethod
    def _is_late_for_taxes(cls, siren_or_siret: str) -> bool:
        # allows to get companies registered at the RCS or not, depending on the third digit in the SIREN/SIRET
        return siren_or_siret[2] == "9"

    @classmethod
    def _get_urssaf_dates(cls) -> tuple[datetime.date, datetime.date]:
        today = datetime.date.today()
        return today - datetime.timedelta(days=31), today + datetime.timedelta(days=151)

    def get_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
        self._check_siren(siren)

        if not self._is_diffusible(siren):
            if raise_if_non_public:
                raise exceptions.NonPublicDataException()
            return models.SirenInfo(
                siren=siren,
                name="[ND]",
                head_office_siret=siren + "00001",
                ape_code="90.01Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code=self._legal_category_code(siren),
                address=self.nd_address if with_address else None,
                active=self._is_active(siren),
                diffusible=False,
            )

        ape_code, ape_label = self._ape_code_and_label(siren)

        return models.SirenInfo(
            siren=siren,
            name="MINISTERE DE LA CULTURE",
            head_office_siret=siren + "00001",
            ape_code=ape_code,
            ape_label=ape_label,
            legal_category_code=self._legal_category_code(siren),
            address=self.address if with_address else None,
            active=self._is_active(siren),
            diffusible=True,
        )

    def get_siret(self, siret: str, raise_if_non_public: bool = False) -> models.SiretInfo:
        assert len(siret) == 14

        self._check_siren(siret[:9])

        ape_code, ape_label = self._ape_code_and_label(siret)

        # allows to get a non-diffusible offerer in dev/testing environments: any SIRET which starts with '9'
        if not self._is_diffusible(siret):
            if raise_if_non_public:
                raise exceptions.NonPublicDataException()
            return models.SiretInfo(
                siret=siret,
                active=self._is_active(siret),
                diffusible=False,
                name="[ND]",
                address=self.nd_address,
                ape_code=ape_code,
                ape_label=ape_label,
                legal_category_code=self._legal_category_code(siret),
            )

        return models.SiretInfo(
            siret=siret,
            active=self._is_active(siret),
            diffusible=True,
            name="MINISTERE DE LA CULTURE",
            address=self.address,
            ape_code=ape_code,
            ape_label=ape_label,
            legal_category_code=self._legal_category_code(siret),
        )

    def get_rcs(self, siren: str) -> models.RCSInfo:
        try:
            self._check_siren(siren)
        except exceptions.UnknownEntityException:
            return models.RCSInfo(registered=False)

        if not self._is_commercial(siren):
            return models.RCSInfo(registered=False)

        return models.RCSInfo(
            registered=True,
            registration_date=datetime.date(2023, 1, 2),
            deregistration_date=None if self._is_active(siren) else datetime.date(2023, 12, 31),
            head_office_activity="TEST",
        )

    def get_urssaf(self, siren: str) -> models.UrssafInfo:
        self._check_siren(siren)

        if self._is_late_for_taxes(siren):
            return models.UrssafInfo(
                attestation_delivered=False,
                details="La délivrance de l'attestation de vigilance a été refusée par l'Urssaf car l'entité n'est pas "
                "à jour de ses cotisations sociales.",
            )

        validity_dates = self._get_urssaf_dates()

        return models.UrssafInfo(
            attestation_delivered=True,
            details="La délivrance de l'attestation de vigilance a été validée par l'Urssaf. L'attestation est "
            "délivrée lorsque l'entité est à jour de ses cotisations et contributions, ou bien dans le cas de "
            "situations spécifiques détaillées dans la documentation métier.",
            validity_start_date=validity_dates[0],
            validity_end_date=validity_dates[1],
            verification_code="ABCD1234EFGH567",
        )

    def get_dgfip(self, siren: str) -> models.DgfipInfo:
        self._check_siren(siren)

        if self._is_late_for_taxes(siren):
            return models.DgfipInfo(attestation_delivered=False)

        return models.DgfipInfo(
            attestation_delivered=True,
            attestation_date=datetime.date.today(),
            verified_date=datetime.date.today() - datetime.timedelta(days=10),
        )
