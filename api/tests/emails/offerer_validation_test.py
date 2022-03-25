import secrets

from bs4 import BeautifulSoup

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.mailing import make_offerer_internal_validation_email


def get_by_siren_stub(offerer):
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
        "other_etablissements_sirets": ["39525144000032", "39525144000065"],
    }


def test_write_object_validation_email():
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
    email = make_offerer_internal_validation_email(offerer, user_offerer, get_by_siren=get_by_siren_stub)

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

    offerer_section = html.select_one("section[data-testId='offerer']")
    assert offerer_section.h2.text == "Nouvelle structure :"
    assert offerer_section.h3.text == "Infos API entreprise :"
    assert offerer_section.strong.a["href"] == "http://localhost:5001/validate/offerer/{}".format(
        offerer.validationToken
    )
    assert offerer_section.strong.a.text == "cliquez ici"

    user_offerer_section = html.select_one("section[data-testId='user_offerer']")
    assert user_offerer_section.h2.text == "Nouveau rattachement :"
    assert user_offerer_section.h3.text == "Utilisateur :"
    assert user_offerer_section.strong.a["href"] == "http://localhost:5001/validate/user-offerer/{}".format(
        user_offerer.validationToken
    )
    assert user_offerer_section.strong.a.text == "cliquez ici"

    offerer_data = offerer_section.select_one("pre.offerer-data").text
    assert "'address': '122 AVENUE DE FRANCE'" in offerer_data
    assert "'city': 'Paris'" in offerer_data
    assert "'name': 'Accenture'" in offerer_data
    assert "'postalCode': '75013'" in offerer_data
    assert "'siren': '732075312'" in offerer_data
    assert "'validationToken': '{}'".format(validation_token) in offerer_data

    api_entreprise_data = offerer_section.select_one("pre.api-entreprise-data").text
    assert "'other_etablissements_sirets':['39525144000032','39525144000065']" in api_entreprise_data.replace(
        " ", ""
    ).replace("\n", "")
    assert "etablissement_siege" in api_entreprise_data


def test_validation_email_object_does_not_include_validation_link_if_user_offerer_is_already_validated(app):
    user_offerer = offerers_factories.UserOffererFactory.build()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
        get_by_siren=get_by_siren_stub,
    )

    html = BeautifulSoup(email.html_content, features="html.parser")
    assert "Nouveau rattachement :" not in [h2.text for h2 in html.select("section[data-testId='summary'] h2")]
    assert not html.select("section[data-testId='user_offerer'] strong.validation a")
    assert html.select("section[data-testId='user_offerer'] h2")[0].text == "Rattachement :"


def test_validation_email_object_does_not_include_validation_link_if_offerer_is_already_validated():
    user_offerer = offerers_factories.UserOffererFactory.build()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
        get_by_siren=get_by_siren_stub,
    )

    html = BeautifulSoup(email.html_content, features="html.parser")
    assert "Nouvelle structure :" not in [h2.text for h2 in html.select("section[data-testId='summary'] h2")]
    assert not html.select("section[data-testId='offerer'] strong.validation a")
    assert html.select("section[data-testId='offerer'] h2")[0].text == "Structure :"


def test_validation_email_should_neither_return_clearTextPassword_nor_totallysafepsswd():
    user_offerer = offerers_factories.UserOffererFactory.build()
    email = make_offerer_internal_validation_email(
        user_offerer.offerer,
        user_offerer,
        get_by_siren=get_by_siren_stub,
    )

    email_html_soup = BeautifulSoup(email.html_content, features="html.parser")
    assert "clearTextPassword" not in str(email_html_soup)
    assert "totallysafepsswd" not in str(email_html_soup)


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
        get_by_siren=get_by_siren_stub,
    )

    # Then
    assert email_object.subject == "95 - inscription / rattachement PRO à valider : Le Petit Rintintin"
