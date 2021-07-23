import secrets

from bs4 import BeautifulSoup
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.utils.mailing import make_validation_email_object

from tests.utils.mailing_test import get_by_siren_stub


@pytest.mark.usefixtures("db_session")
def test_write_object_validation_email(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(
        idx=123,
        siren="732075312",
        address="122 AVENUE DE FRANCE",
        city="Paris",
        postal_code="75013",
        name="Accenture",
        validation_token=validation_token,
    )

    user = users_factories.UserFactory.build(
        isBeneficiary=False,
        departementCode="75",
        email="user@accenture.com",
        publicName="Test",
        validationToken=validation_token,
    )

    user_offerer = create_user_offerer(user=user, offerer=offerer, validation_token=validation_token)

    # When
    email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_by_siren_stub)

    # Then
    html = BeautifulSoup(email["Html-part"], features="html.parser")
    assert html.h1.text == "Inscription ou rattachement PRO à valider"

    summary_section = html.select_one("section[data-testId='summary']")
    assert summary_section.select("h2")[0].a.text == "Structure :"
    assert summary_section.select("h2")[0].a["href"] == "http://localhost:3001/accueil?structure=PM"
    assert summary_section.select("h2")[1].text == "Utilisateur :"
    assert summary_section.select("h2")[2].text == "Nouveau rattachement :"
    assert summary_section.select("strong")[0].a["href"] == "http://localhost:5000/validate/user-offerer/{}".format(
        user_offerer.validationToken
    )
    assert summary_section.select("strong")[0].a.text == "cliquez ici"
    assert summary_section.select("h2")[3].text == "Nouvelle structure :"
    assert summary_section.select("strong")[1].a["href"] == "http://localhost:5000/validate/offerer/{}".format(
        offerer.validationToken
    )
    assert summary_section.select("strong")[1].a.text == "cliquez ici"

    offerer_section = html.select_one("section[data-testId='offerer']")
    assert offerer_section.h2.text == "Nouvelle structure :"
    assert offerer_section.h3.text == "Infos API entreprise :"
    assert offerer_section.strong.a["href"] == "http://localhost:5000/validate/offerer/{}".format(
        offerer.validationToken
    )
    assert offerer_section.strong.a.text == "cliquez ici"

    user_offerer_section = html.select_one("section[data-testId='user_offerer']")
    assert user_offerer_section.h2.text == "Nouveau rattachement :"
    assert user_offerer_section.h3.text == "Utilisateur :"
    assert user_offerer_section.strong.a["href"] == "http://localhost:5000/validate/user-offerer/{}".format(
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


@pytest.mark.usefixtures("db_session")
def test_validation_email_object_does_not_include_validation_link_if_user_offerer_is_already_validated(app):
    # Given
    offerer = create_offerer()
    user = users_factories.UserFactory.build()
    user_offerer = create_user_offerer(user, offerer)

    # When
    email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_by_siren_stub)

    # Then
    html = BeautifulSoup(email["Html-part"], features="html.parser")
    assert "Nouveau rattachement :" not in [h2.text for h2 in html.select("section[data-testId='summary'] h2")]
    assert not html.select("section[data-testId='user_offerer'] strong.validation a")
    assert html.select("section[data-testId='user_offerer'] h2")[0].text == "Rattachement :"


@pytest.mark.usefixtures("db_session")
def test_validation_email_object_does_not_include_validation_link_if_offerer_is_already_validated(app):
    # Given
    offerer = create_offerer(idx=123)
    user = users_factories.UserFactory.build()
    user_offerer = create_user_offerer(user=user, offerer=offerer)

    # When
    email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_by_siren_stub)

    # Then
    html = BeautifulSoup(email["Html-part"], features="html.parser")
    assert "Nouvelle structure :" not in [h2.text for h2 in html.select("section[data-testId='summary'] h2")]
    assert not html.select("section[data-testId='offerer'] strong.validation a")
    assert html.select("section[data-testId='offerer'] h2")[0].text == "Structure :"


@pytest.mark.usefixtures("db_session")
def test_validation_email_should_neither_return_clearTextPassword_nor_totallysafepsswd(app):
    # Given
    offerer = create_offerer()
    user = users_factories.UserFactory.build()
    user_offerer = create_user_offerer(user=user, offerer=offerer)

    mocked_api_entreprises = get_by_siren_stub

    # When
    email = make_validation_email_object(offerer, user_offerer, get_by_siren=mocked_api_entreprises)

    # Then
    email_html_soup = BeautifulSoup(email["Html-part"], features="html.parser")
    assert "clearTextPassword" not in str(email_html_soup)
    assert "totallysafepsswd" not in str(email_html_soup)
