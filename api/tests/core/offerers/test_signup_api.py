import pytest

from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import TargetAudience
from pcapi.core.offerers.structure_signup_api import BOOKSTORE_MESSAGE
from pcapi.core.offerers.structure_signup_api import COLLECTIVE_MESSAGE
from pcapi.core.offerers.structure_signup_api import UNUSUAL_APE_CODE_MESSAGE
from pcapi.core.offerers.structure_signup_api import EligibilityDocument
from pcapi.core.offerers.structure_signup_api import get_signup_documents_and_messages


pytestmark = pytest.mark.usefixtures("db_session")

SAS_CATEGORY_CODE = "5710"
SINGLE_CATEGORY_CODE = "1000"
APE_CODE = "9003A"  # "Création artistique", in whitelist
APE_CODE_BOOKSTORE = "5810Z"
APE_CODE_UNUSUAL = "1911Z"


class SignupSimulationTest:
    def test_standard_case(self):
        """not a single member structure, not a bookstore / recording studio, whitelist ape code"""

        response = get_signup_documents_and_messages(
            ape_code=APE_CODE,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=Activity.OTHER,
        )

        assert response.documents == [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION]
        assert response.messages == []

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity",
        [
            pytest.param(
                "8411Z",
                SAS_CATEGORY_CODE,
                Activity.OTHER,
                id="Administration publique générale, code ape 1",
            ),
            pytest.param(
                "8411Y",
                SAS_CATEGORY_CODE,
                Activity.OTHER,
                id="Administration publique générale, code ape 2",
            ),
            pytest.param(
                "8542Z",
                SAS_CATEGORY_CODE,
                Activity.OTHER,
                id="Enseignement supérieur, code ape 1",
            ),
            pytest.param(
                "8540Y",
                SAS_CATEGORY_CODE,
                Activity.OTHER,
                id="Enseignement supérieur, code ape 2",
            ),
            pytest.param(
                "1111C",
                "7312",
                Activity.OTHER,
                id="Etablissement Public National",
            ),
            pytest.param(
                "8411Z",
                "7312",
                Activity.OTHER,
                id="Administration publique générale + Etablissement Public National",
            ),
            pytest.param(
                "8411Z",
                SAS_CATEGORY_CODE,
                Activity.BOOKSTORE,
                id="Administration publique générale + librairie",
            ),
            pytest.param(
                APE_CODE_UNUSUAL,
                "7312",
                Activity.RADIO_OR_MUSIC_STREAMING,
                id="Etablissement public national + code ape hors whitelist + studio",
            ),
        ],
    )
    def test_mandated_structures(self, ape_code: str, legal_category_code: str, activity: str):
        """Commune ou collectivité territoriale (Administration publique générale) OU Enseignement supérieur OU Etablissement Public National"""

        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == [EligibilityDocument.WEBSITE]
        assert response.messages == []

        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=True,
            targets=[TargetAudience.COLLECTIVE],
            activity=activity,
        )

        assert response.documents == [EligibilityDocument.WEBSITE]
        assert response.messages == [COLLECTIVE_MESSAGE]

    @pytest.mark.parametrize(
        "ape_code, activity",
        [
            pytest.param("5920Z", Activity.RECORD_STORE, id="Studio d'enregistrement code ape 1"),
            pytest.param("5920Y", Activity.RECORD_STORE, id="Studio d'enregistrement code ape 2"),
            pytest.param(
                "5920Z",
                Activity.ARTISTIC_PRACTICE,
                id="Studio d'enregistrement, activité contact mineur",
            ),
        ],
    )
    def test_sound_studio(self, ape_code: str, activity: str):
        expected_documents = [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]

        # target INDIVIDUAL
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == expected_documents
        assert response.messages == []

        # target COLLECTIVE
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.COLLECTIVE],
            activity=activity,
        )

        assert response.documents == expected_documents
        assert response.messages == [COLLECTIVE_MESSAGE]

        # single member structure
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == [*expected_documents, EligibilityDocument.CRIMINAL_RECORDS]
        assert response.messages == []

    @pytest.mark.parametrize(
        "ape_code, legal_category_code, activity, documents, messages",
        [
            pytest.param(
                APE_CODE,
                SAS_CATEGORY_CODE,
                Activity.BOOKSTORE,
                [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION],
                [BOOKSTORE_MESSAGE],
                id="Activité librairie",
            ),
            pytest.param(
                APE_CODE,
                SAS_CATEGORY_CODE,
                Activity.PUBLISHING_HOUSE,
                [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION],
                [BOOKSTORE_MESSAGE],
                id="Activité maison d'édition",
            ),
            pytest.param(
                APE_CODE_BOOKSTORE,
                SAS_CATEGORY_CODE,
                Activity.OTHER,
                [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION],
                [BOOKSTORE_MESSAGE],
                id="Code ape librairie, autre activité",
            ),
            pytest.param(
                APE_CODE_UNUSUAL,
                SAS_CATEGORY_CODE,
                Activity.BOOKSTORE,
                [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION],
                [UNUSUAL_APE_CODE_MESSAGE, BOOKSTORE_MESSAGE],
                id="Activité librairie, code ape hors whitelist",
            ),
            pytest.param(
                APE_CODE_BOOKSTORE,
                SINGLE_CATEGORY_CODE,
                Activity.BOOKSTORE,
                [
                    EligibilityDocument.WEBSITE,
                    EligibilityDocument.DESCRIPTION,
                    EligibilityDocument.RESUME_OR_PORTFOLIO,
                    EligibilityDocument.DIPLOMAS,
                ],
                [BOOKSTORE_MESSAGE],
                id="Activité librairie, uninominal",
            ),
            pytest.param(
                APE_CODE_BOOKSTORE,
                SINGLE_CATEGORY_CODE,
                Activity.OTHER,
                [
                    EligibilityDocument.WEBSITE,
                    EligibilityDocument.DESCRIPTION,
                    EligibilityDocument.RESUME_OR_PORTFOLIO,
                    EligibilityDocument.DIPLOMAS,
                    EligibilityDocument.CRIMINAL_RECORDS,
                ],
                [BOOKSTORE_MESSAGE],
                id="Code ape librairie, autre activité, uninominal",
            ),
        ],
    )
    def test_bookstore(self, ape_code: str, legal_category_code: str, activity: str, documents: list, messages: list):
        # target INDIVIDUAL
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=False,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == documents
        assert response.messages == messages

        # target COLLECTIVE
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=False,
            targets=[TargetAudience.COLLECTIVE],
            activity=activity,
        )

        assert response.documents == documents
        assert response.messages == [COLLECTIVE_MESSAGE, *messages]

        # open to public
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == [*documents, EligibilityDocument.SHOP_PICTURES]
        assert response.messages == messages

    @pytest.mark.parametrize(
        "ape_code, activity, messages, additional_documents",
        [
            pytest.param(APE_CODE, Activity.FESTIVAL, [], [], id="Code ape whitelist"),
            pytest.param(
                APE_CODE,
                Activity.OTHER,
                [],
                [EligibilityDocument.CRIMINAL_RECORDS],
                id="Code ape whitelist, activité contact mineur",
            ),
            pytest.param(
                APE_CODE_UNUSUAL,
                Activity.FESTIVAL,
                [UNUSUAL_APE_CODE_MESSAGE],
                [],
                id="Code ape hors whitelist",
            ),
            pytest.param(
                APE_CODE_UNUSUAL,
                Activity.OTHER,
                [UNUSUAL_APE_CODE_MESSAGE],
                [EligibilityDocument.CRIMINAL_RECORDS],
                id="Code ape hors whitelist, activité contact mineur",
            ),
        ],
    )
    def test_single_member_structure(self, ape_code: str, activity: str, messages: list, additional_documents: list):
        documents = [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
            *additional_documents,
        ]

        # target INDIVIDUAL
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.INDIVIDUAL],
            activity=activity,
        )

        assert response.documents == documents
        assert response.messages == messages

        # target COLLECTIVE
        response = get_signup_documents_and_messages(
            ape_code=ape_code,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            targets=[TargetAudience.COLLECTIVE],
            activity=activity,
        )

        assert response.documents == documents
        assert response.messages == [COLLECTIVE_MESSAGE, *messages]
