import secrets
from unittest import mock

from bs4 import BeautifulSoup

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.utils.mailing import make_offerer_internal_validation_email


def get_by_offerer_stub(offerer):
    return {
        "unite_legale": {
            "siren": "395251440",
            "etablissement_siege": {
                "siren": "395251440",
                "siret": "39525144000016",
                "etablissement_siege": "true",
            },
            "activite_principale": "59.14Z",
        },
    }


@override_features(USE_INSEE_SIRENE_API=True)
def test_write_object_validation_email():
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = offerers_factories.OffererFactory.build(
        id=123,
        validationToken=validation_token,
    )

    user = users_factories.ProFactory.build()

    user_offerer = offerers_factories.UserOffererFactory.build(
        user=user,
        offerer=offerer,
        validationToken=validation_token,
    )

    # When
    email = make_offerer_internal_validation_email(offerer, user_offerer)

    # Then
    html = BeautifulSoup(email.html_content, features="html.parser")
    assert html.h1.text == "Inscription ou rattachement PRO à valider"

    summary_section = html.select_one("section[data-testId='summary']")
    assert summary_section.select("h2")[0].a.text == "Structure :"
    assert summary_section.select("h2")[0].a["href"] == "http://localhost:3001/accueil?structure=PM"
    assert summary_section.select("h2")[1].text == "Utilisateur :"
    assert summary_section.select("h2")[2].text == "Nouveau rattachement :"
    assert summary_section.select("strong")[0].a["href"] == "http://localhost:5001/validate/user-offerer/{}".format(
        user_offerer.validationToken
    )
    assert summary_section.select("strong")[0].a.text == "cliquez ici"
    assert summary_section.select("h2")[3].text == "Nouvelle structure :"
    assert summary_section.select("strong")[1].a["href"] == "http://localhost:5001/validate/offerer/{}".format(
        offerer.validationToken
    )
    assert summary_section.select("strong")[1].a.text == "cliquez ici"

    api_entreprise_data = html.select_one("pre.api-entreprise-data").text
    assert "ape_code" in api_entreprise_data


@override_features(USE_INSEE_SIRENE_API=False)
@mock.patch("pcapi.connectors.api_entreprises.get_by_offerer", get_by_offerer_stub)
def test_write_object_validation_email_legacy():
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = offerers_factories.OffererFactory.build(
        id=123,
        siren="732075312",
        address="122 AVENUE DE FRANCE",
        city="Paris",
        postalCode="75013",
        name="Accenture",
        validationToken=validation_token,
    )

    user = users_factories.ProFactory.build(
        departementCode="75",
        email="user@accenture.com",
        publicName="Test",
        validationToken=validation_token,
    )

    user_offerer = offerers_factories.UserOffererFactory.build(
        user=user,
        offerer=offerer,
        validationToken=validation_token,
    )

    # When
    email = make_offerer_internal_validation_email(offerer, user_offerer)
    # Then
    html = BeautifulSoup(email.html_content, features="html.parser")
    assert html.h1.text == "Inscription ou rattachement PRO à valider"

    summary_section = html.select_one("section[data-testId='summary']")
    assert summary_section.select("h2")[0].a.text == "Structure :"
    assert summary_section.select("h2")[0].a["href"] == "http://localhost:3001/accueil?structure=PM"
    assert summary_section.select("h2")[1].text == "Utilisateur :"
    assert summary_section.select("h2")[2].text == "Nouveau rattachement :"
    assert summary_section.select("strong")[0].a["href"] == "http://localhost:5001/validate/user-offerer/{}".format(
        user_offerer.validationToken
    )
    assert summary_section.select("strong")[0].a.text == "cliquez ici"
    assert summary_section.select("h2")[3].text == "Nouvelle structure :"
    assert summary_section.select("strong")[1].a["href"] == "http://localhost:5001/validate/offerer/{}".format(
        offerer.validationToken
    )
    assert summary_section.select("strong")[1].a.text == "cliquez ici"

    api_entreprise_data = html.select_one("pre.api-entreprise-data").text
    assert "etablissement_siege" in api_entreprise_data


@mock.patch("pcapi.connectors.api_entreprises.get_by_offerer", get_by_offerer_stub)
def test_no_validation_link_if_user_offerer_is_already_validated():
    user_offerer = offerers_factories.UserOffererFactory.build()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
    )
    assert "Nouveau rattachement :" not in email.html_content


@mock.patch("pcapi.connectors.api_entreprises.get_by_offerer", get_by_offerer_stub)
def test_no_validation_link_if_offerer_is_already_validated():
    user_offerer = offerers_factories.UserOffererFactory.build()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
    )
    assert "Nouvelle structure :" not in email.html_content


@mock.patch("pcapi.connectors.api_entreprises.get_by_offerer", get_by_offerer_stub)
def test_should_return_subject_with_correct_departement_code():
    # Given
    user_offerer = offerers_factories.UserOffererFactory.build(
        offerer__name="Le Petit Rintintin",
        offerer__postalCode="95000",
    )

    # When
    email_object = make_offerer_internal_validation_email(
        user_offerer=user_offerer,
        offerer=user_offerer.offerer,
    )

    # Then
    assert email_object.subject == "95 - inscription / rattachement PRO à valider : Le Petit Rintintin"
