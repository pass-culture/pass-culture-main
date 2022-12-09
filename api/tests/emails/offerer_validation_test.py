from bs4 import BeautifulSoup

from pcapi.connectors import sirene
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.mailing import make_offerer_internal_validation_email


def generate_siren_info() -> sirene.SirenInfo:
    return sirene.SirenInfo(
        siren="123456789",
        name="whatever",
        head_office_siret="12345678900001",
        ape_code="16.64Z",
        legal_category_code="???",
        address=None,
    )


def test_write_object_validation_email():
    # Given
    offerer = offerers_factories.NotValidatedOffererFactory.build(id=123)

    user = users_factories.ProFactory.build()

    user_offerer = offerers_factories.NotValidatedUserOffererFactory.build(user=user, offerer=offerer)

    siren_info = generate_siren_info()

    # When
    email = make_offerer_internal_validation_email(offerer, user_offerer, siren_info)

    # Then
    html = BeautifulSoup(email.html_content, features="html.parser")
    assert html.h1.text == "Inscription ou rattachement PRO à valider"

    summary_section = html.select_one("section[data-testId='summary']")
    assert summary_section.select("h2")[0].a.text == "Structure :"
    assert summary_section.select("h2")[0].a["href"] == "http://localhost:3001/accueil?structure=PM"
    assert summary_section.select("h2")[1].text == "Utilisateur :"
    assert summary_section.select("h2")[2].text == "Nouveau rattachement :"
    assert summary_section.select("h2")[3].text == "Nouvelle structure :"

    api_entreprise_data = html.select_one("pre.api-entreprise-data").text
    assert "ape_code" in api_entreprise_data


def test_no_validation_link_if_user_offerer_is_already_validated():
    user_offerer = offerers_factories.UserOffererFactory.build()
    siren_info = generate_siren_info()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
        siren_info,
    )
    assert "Nouveau rattachement :" not in email.html_content


def test_no_validation_link_if_offerer_is_already_validated():
    user_offerer = offerers_factories.UserOffererFactory.build()
    siren_info = generate_siren_info()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
        siren_info,
    )
    assert "Nouvelle structure :" not in email.html_content


def test_should_return_subject_with_correct_departement_code():
    # Given
    user_offerer = offerers_factories.UserOffererFactory.build(
        offerer__name="Le Petit Rintintin",
        offerer__postalCode="95000",
    )
    siren_info = generate_siren_info()

    # When
    email_object = make_offerer_internal_validation_email(
        user_offerer=user_offerer,
        offerer=user_offerer.offerer,
        siren_info=siren_info,
    )

    # Then
    assert email_object.subject == "95 - inscription / rattachement PRO à valider : Le Petit Rintintin"
