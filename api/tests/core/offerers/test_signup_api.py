import pytest

from pcapi import settings
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import StructureSimulationInfo
from pcapi.core.offerers.models import TargetAudience
from pcapi.core.offerers.structure_signup_api import BOOKSTORE_MESSAGE
from pcapi.core.offerers.structure_signup_api import COLLECTIVE_MESSAGE
from pcapi.core.offerers.structure_signup_api import MINOR_CONTACT_ACTIVITIES
from pcapi.core.offerers.structure_signup_api import UNUSUAL_APE_CODE_MESSAGE
from pcapi.core.offerers.structure_signup_api import EligibilityDocument
from pcapi.core.offerers.structure_signup_api import build_signup_link
from pcapi.core.offerers.structure_signup_api import get_signup_documents
from pcapi.core.offerers.structure_signup_api import get_signup_messages


pytestmark = pytest.mark.usefixtures("db_session")

SAS_CATEGORY_CODE = "5710"
SINGLE_CATEGORY_CODE = "1000"
APE_CODE = "9003A"  # "Création artistique", in whitelist
APE_CODE_BOOKSTORE = "5810Z"
APE_CODE_UNUSUAL = "1911Z"


class SignupDocumentsTest:
    def test_standard_case(self):
        """not a single member structure, not a bookstore / recording studio, whitelist ape code"""

        documents = get_signup_documents(
            ape_code=APE_CODE,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            activity=Activity.OTHER,
        )
        assert documents == [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION]

    @pytest.mark.parametrize(
        "ape_code, legal_category_code",
        [
            pytest.param("8411Z", SAS_CATEGORY_CODE, id="Administration publique générale, code ape 1"),
            pytest.param("8411Y", SAS_CATEGORY_CODE, id="Administration publique générale, code ape 2"),
            pytest.param("8542Z", SAS_CATEGORY_CODE, id="Enseignement supérieur, code ape 1"),
            pytest.param("8540Y", SAS_CATEGORY_CODE, id="Enseignement supérieur, code ape 2"),
            pytest.param("1111C", "7312", id="Etablissement Public National"),
            pytest.param("8411Z", "7312", id="Administration publique générale + Etablissement Public National"),
        ],
    )
    def test_mandated_structures(self, ape_code: str, legal_category_code: str):
        """Commune ou collectivité territoriale (Administration publique générale) OU Enseignement supérieur OU Etablissement Public National"""

        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=legal_category_code,
            is_open_to_public=True,
            activity=Activity.OTHER,
        )
        assert documents == [EligibilityDocument.WEBSITE]

    @pytest.mark.parametrize(
        "ape_code, activity",
        [
            pytest.param("5920Z", Activity.RECORD_STORE, id="Studio d'enregistrement code ape 1"),
            pytest.param("5920Y", Activity.RECORD_STORE, id="Studio d'enregistrement code ape 2"),
            pytest.param("5920Z", Activity.ARTISTIC_PRACTICE, id="Studio d'enregistrement, activité contact mineur"),
        ],
    )
    def test_sound_studio(self, ape_code: str, activity: Activity):
        expected_documents = [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]

        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == expected_documents

        # single member structure
        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == [*expected_documents, EligibilityDocument.CRIMINAL_RECORDS]

    @pytest.mark.parametrize(
        "ape_code, activity",
        [
            pytest.param(APE_CODE, Activity.BOOKSTORE, id="Activité librairie"),
            pytest.param(APE_CODE, Activity.PUBLISHING_HOUSE, id="Activité maison d'édition"),
            pytest.param(APE_CODE_BOOKSTORE, Activity.ARTS_CENTRE, id="Code ape librairie"),
        ],
    )
    def test_bookstore(self, ape_code: str, activity: Activity):
        # not open to public
        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=False,
            activity=activity,
        )
        assert documents == [EligibilityDocument.WEBSITE, EligibilityDocument.DESCRIPTION]

        # open to public
        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=SAS_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.SHOP_PICTURES,
        ]

        # single member structure
        documents = get_signup_documents(
            ape_code=ape_code,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
            EligibilityDocument.SHOP_PICTURES,
        ]

    def test_bookstore_single_member_minor_contact(self):
        documents = get_signup_documents(
            ape_code=APE_CODE_BOOKSTORE,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            activity=Activity.OTHER,
        )
        assert documents == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
            EligibilityDocument.CRIMINAL_RECORDS,
            EligibilityDocument.SHOP_PICTURES,
        ]

    @pytest.mark.parametrize(
        "activity", set(Activity) - MINOR_CONTACT_ACTIVITIES - {Activity.BOOKSTORE, Activity.PUBLISHING_HOUSE}
    )
    def test_single_member_structure(self, activity: Activity):
        documents = get_signup_documents(
            ape_code=APE_CODE,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
        ]

    @pytest.mark.parametrize("activity", MINOR_CONTACT_ACTIVITIES)
    def test_single_member_structure_minor_contact(self, activity: Activity):
        documents = get_signup_documents(
            ape_code=APE_CODE,
            legal_category_code=SINGLE_CATEGORY_CODE,
            is_open_to_public=True,
            activity=activity,
        )
        assert documents == [
            EligibilityDocument.WEBSITE,
            EligibilityDocument.DESCRIPTION,
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.DIPLOMAS,
            EligibilityDocument.CRIMINAL_RECORDS,
        ]


class SignupMessagesTest:
    def test_no_messages(self):
        messages = get_signup_messages(ape_code=APE_CODE, targets=[TargetAudience.INDIVIDUAL], activity=Activity.OTHER)
        assert messages == []

    def test_messages_collective(self):
        messages = get_signup_messages(ape_code=APE_CODE, targets=[TargetAudience.COLLECTIVE], activity=Activity.OTHER)
        assert messages == [COLLECTIVE_MESSAGE]

        messages = get_signup_messages(
            ape_code=APE_CODE, targets=[TargetAudience.INDIVIDUAL, TargetAudience.COLLECTIVE], activity=Activity.OTHER
        )
        assert messages == [COLLECTIVE_MESSAGE]

    def test_messages_unusual_ape(self):
        messages = get_signup_messages(
            ape_code=APE_CODE_UNUSUAL, targets=[TargetAudience.INDIVIDUAL], activity=Activity.OTHER
        )
        assert messages == [UNUSUAL_APE_CODE_MESSAGE]

    def test_messages_bookstore(self):
        # activity BOOKSTORE
        messages = get_signup_messages(
            ape_code=APE_CODE, targets=[TargetAudience.INDIVIDUAL], activity=Activity.BOOKSTORE
        )
        assert messages == [BOOKSTORE_MESSAGE]

        # # activity PUBLISHING_HOUSE
        messages = get_signup_messages(
            ape_code=APE_CODE, targets=[TargetAudience.INDIVIDUAL], activity=Activity.PUBLISHING_HOUSE
        )
        assert messages == [BOOKSTORE_MESSAGE]

        # ape code
        messages = get_signup_messages(
            ape_code=APE_CODE_BOOKSTORE, targets=[TargetAudience.INDIVIDUAL], activity=Activity.OTHER
        )
        assert messages == [BOOKSTORE_MESSAGE]

    def test_all_messages(self):
        messages = get_signup_messages(
            ape_code=APE_CODE_UNUSUAL, targets=[TargetAudience.COLLECTIVE], activity=Activity.BOOKSTORE
        )
        assert messages == [COLLECTIVE_MESSAGE, UNUSUAL_APE_CODE_MESSAGE, BOOKSTORE_MESSAGE]


class BuildSignupLinkTest:
    def test_build(self):
        link = build_signup_link(
            structure_simulation_info=StructureSimulationInfo(
                siret="44285836100029",
                is_open_to_public=True,
                targets=[TargetAudience.INDIVIDUAL],
                activity=Activity.LIBRARY,
            )
        )

        assert (
            link
            == f"{settings.PRO_URL}/inscription/compte/creation?siret=44285836100029&isOpenToPublic=true&targets=INDIVIDUAL&activity=LIBRARY"
        )

    def test_build_multiple_targets(self):
        link = build_signup_link(
            structure_simulation_info=StructureSimulationInfo(
                siret="44285836100029",
                is_open_to_public=False,
                targets=[TargetAudience.INDIVIDUAL, TargetAudience.COLLECTIVE],
                activity=Activity.OTHER,
            )
        )

        assert (
            link
            == f"{settings.PRO_URL}/inscription/compte/creation?siret=44285836100029&isOpenToPublic=false&targets=INDIVIDUAL&targets=COLLECTIVE&activity=OTHER"
        )
