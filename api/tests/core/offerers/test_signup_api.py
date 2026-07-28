import pytest

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.structure_signup_api import BOOKSTORE_MESSAGE
from pcapi.core.offerers.structure_signup_api import COLLECTIVE_MESSAGE
from pcapi.core.offerers.structure_signup_api import UNUSUAL_APE_CODE_MESSAGE
from pcapi.core.offerers.structure_signup_api import EligibilityDocument
from pcapi.core.offerers.structure_signup_api import get_signup_documents_and_messages


pytestmark = pytest.mark.usefixtures("db_session")


class SignupSimulationTest:
    def test_eligibility_documents_standard_case(self):
        """structure non-entreprise-individuelle qui n'est ni un libraire ni un studio d'enregistrement, qui ne fait pas d'accompagnement"""
        response = get_signup_documents_and_messages(
            ape_code="AAAAA",
            legal_category_code="BBBBB",
            isOpenToPublic=True,
            targets=[offerers_models.OffererTarget.INDIVIDUAL],
            activity=offerers_models.Activity.OTHER,
        )

        assert response["documents"] == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
        ]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "8411Z",
                "AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Commune ou collectivité territoriale (Administration publique générale)
            (
                "8411Z",
                "AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # Commune ou collectivité territoriale (Administration publique générale) avec collectif
            (
                "8542Z",
                "BBBBB",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Enseignement supérieur
            (
                "CCCCC",
                "73AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Etablissement Public National
            (
                "8411Z",
                "73AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Collectivité + Etablissement Public National
            (
                "8411Z",
                "AAAAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Collectivité + activité librairie > ne doit pas faire les checks librairie
            (
                "8411Z",
                "13AAAAA",
                offerers_models.Activity.ARTISTIC_PRACTICE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Commune ou collectivité territoriale + activité avec warning
            (
                "1911Z",
                "73AAAAA",
                offerers_models.Activity.RADIO_OR_MUSIC_STREAMING,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # Etablissement public national + code ape hors whitelist + activité avec warning
        ],
    )
    def test_eligibility_documents_state_mandated_structures(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        """Commune ou collectivité territoriale (Administration publique générale) OU Enseignement supérieur OU Etablissement Public National"""
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )
        assert response["documents"] == [EligibilityDocument.WEBSITE]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]
        else:
            assert not response["messages"]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "5920Z",
                "AAAAA",
                offerers_models.Activity.RECORD_STORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # studio d'enregistrement
            (
                "5920Z",
                "88888",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # studio avec activité qui n'a rien a voir
            (
                "5920Z",
                "AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # studio d'enregistrement avec warning collectif
        ],
    )
    def test_eligibility_documents_sound_studio(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        """studio d'enregistrement"""
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )

        assert response["documents"] == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]
        else:
            assert not response["messages"]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "5920Z",
                "111111",
                offerers_models.Activity.RECORD_STORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # studio uninomial
            (
                "5920Z",
                "111111",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # studio uninomial avec activité qui n'a rien a voir
            (
                "5920Z",
                "111111",
                offerers_models.Activity.ARTISTIC_PRACTICE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # studio uninomial avec activité avec warning
            (
                "5920Z",
                "111111",
                offerers_models.Activity.RECORD_STORE,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # studio uninomial avec warning collectif
        ],
    )
    def test_eligibility_documents_uninomial_sound_studio(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        """studio d'enregistrement uninomial"""
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )

        assert response["documents"] == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
            EligibilityDocument.CRIMINAL_RECORDS,
        ]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]
        else:
            assert not response["messages"]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "94000",
                "AAAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # librairie
            (
                "94000",
                "AAAAAA",
                offerers_models.Activity.PUBLISHING_HOUSE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # maison d edition
            (
                "5810Z",
                "AA11111",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape de librairie avec autre activité
            (
                "4420Z",
                "AA11111",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape suspect avec activité librairie
            (
                "5810Z",
                "AAAAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # librairie avec volonté d offre collective
        ],
    )
    def test_eligibility_documents_bookstore(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        """point de vente de livres"""
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )

        assert response["documents"] == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.SHOP_PICTURES,
        ]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]

        if ape_code.startswith("44"):
            assert UNUSUAL_APE_CODE_MESSAGE in response["messages"]

        assert BOOKSTORE_MESSAGE in response["messages"]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "5810Z",
                "1AAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # librairie
            (
                "5810Z",
                "1AAAAA",
                offerers_models.Activity.PUBLISHING_HOUSE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # maison d edition
            (
                "5810Z",
                "111111",
                offerers_models.Activity.MUSEUM,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape de librairie avec autre activité
            (
                "5810Z",
                "111111",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape de librairie avec autre activité avecx warning
            (
                "4420Z",
                "111111",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape suspect avec activité librairie
            (
                "5810Z",
                "1AAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # librairie avec volonté d offre collective
            (
                "4410Z",
                "1AAAAA",
                offerers_models.Activity.BOOKSTORE,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),
        ],
    )
    def test_eligibility_documents_uninomial_bookstore(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        """point de vente de livres"""
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )

        if activity == offerers_models.Activity.OTHER:
            assert response["documents"] == [
                EligibilityDocument.WEBSITE,
                EligibilityDocument.DESCRIPTION,
                EligibilityDocument.RESUME_OR_PORTFOLIO,
                EligibilityDocument.DIPLOMAS,
                EligibilityDocument.CRIMINAL_RECORDS,
                EligibilityDocument.SHOP_PICTURES,
            ]
        else:
            assert response["documents"] == [
                EligibilityDocument.WEBSITE,
                EligibilityDocument.DESCRIPTION,
                EligibilityDocument.RESUME_OR_PORTFOLIO,
                EligibilityDocument.DIPLOMAS,
                EligibilityDocument.SHOP_PICTURES,
            ]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]

        if ape_code.startswith("44"):
            assert UNUSUAL_APE_CODE_MESSAGE in response["messages"]

        assert BOOKSTORE_MESSAGE in response["messages"]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, targets",
        [
            (
                "1810Z",
                "1AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape whitelist avec warning activite
            (
                "1810Z",
                "1AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # code ape whitelist avec warning activite et collectif
            (
                "1710Z",
                "1AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.INDIVIDUAL],
            ),  # code ape not whitelist avec warning activite
            (
                "1710Z",
                "1AAAAA",
                offerers_models.Activity.OTHER,
                [offerers_models.OffererTarget.COLLECTIVE],
            ),  # code ape not whitelist avec warning activite et collectif
        ],
    )
    def test_eligibility_documents_uninomial_company(
        self, ape_code: str, legal_category_code: str, activity: str, targets: list[str]
    ):
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            isOpenToPublic=True,
            targets=targets,
            activity=activity,
        )

        assert response["documents"] == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
            EligibilityDocument.CRIMINAL_RECORDS,
        ]

        if targets == [offerers_models.OffererTarget.COLLECTIVE]:
            assert COLLECTIVE_MESSAGE in response["messages"]

        if ape_code.startswith("17"):
            assert UNUSUAL_APE_CODE_MESSAGE in response["messages"]

        if targets != [offerers_models.OffererTarget.COLLECTIVE] and ape_code.startswith("18"):
            assert not response["messages"]
