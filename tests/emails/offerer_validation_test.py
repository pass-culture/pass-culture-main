import secrets

from bs4 import BeautifulSoup

from tests.conftest import clean_database, mocked_mail
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer
from tests.utils.mailing_test import get_mocked_response_status_200
from utils.mailing import make_validation_email_object


class WriteObjectValidationEmailTest:
    @mocked_mail
    @clean_database
    def test_write_object_validation_email(app):
        # Given
        validation_token = secrets.token_urlsafe(20)
        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=validation_token)

        user = create_user(can_book_free_offers=False, departement_code='75', email='user@accenture.com',
                           public_name='Test', validation_token=validation_token)

        user_offerer = create_user_offerer(user=user, offerer=offerer, validation_token=validation_token)

        # When
        email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

        # Then
        html = BeautifulSoup(email['Html-part'], features="html.parser")
        assert html.h1.text == 'Inscription ou rattachement PRO à valider'

        div_offerer = html.select('div.offerer')[0]
        assert div_offerer.h2.text == 'Nouvelle structure :'
        assert div_offerer.h3.text == 'Infos API entreprise :'
        assert div_offerer.strong.a['href'] == 'http://localhost/validate?modelNames=Offerer&token={}'.format(
            offerer.validationToken)
        assert div_offerer.strong.a.text == 'cliquez ici'

        div_user_offerer = html.select('div.user_offerer')[0]
        assert div_user_offerer.h2.text == 'Nouveau rattachement :'
        assert div_user_offerer.h3.text == 'Utilisateur :'
        assert div_user_offerer.strong.a['href'] == 'http://localhost/validate?modelNames=UserOfferer&token={}'.format(
            user_offerer.validationToken)
        assert div_user_offerer.strong.a.text == 'cliquez ici'

        offerer_data = div_offerer.select('pre.offerer-data')[0].text
        assert "'address': '122 AVENUE DE FRANCE'" in offerer_data
        assert "'city': 'Paris'" in offerer_data
        assert "'name': 'Accenture'" in offerer_data
        assert "'postalCode': '75013'" in offerer_data
        assert "'siren': '732075312'" in offerer_data
        assert "'validationToken': '{}'".format(validation_token) in offerer_data

        api_entreprise_data = div_offerer.select('pre.api-entreprise-data')[0].text
        assert "'numero_tva_intra': 'FR60732075312'" in api_entreprise_data
        assert "'other_etablissements_sirets': ['73207531200213', '73207531200197', '73207531200171']".replace(' ',
                                                                                                               '').replace(
            '\n', '') in api_entreprise_data.replace(' ', '').replace('\n', '')
        assert 'siege_social' in api_entreprise_data


    @mocked_mail
    @clean_database
    def test_validation_email_object_does_not_include_validation_link_if_user_offerer_is_already_validated(app):
        # Given
        validation_token = secrets.token_urlsafe(20)
        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=validation_token)

        user = create_user(can_book_free_offers=False, departement_code='75', email='user@accenture.com',
                           public_name='Test', validation_token=validation_token)

        user_offerer = create_user_offerer(user, offerer, validation_token=None)

        # When
        email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

        # Then
        html = BeautifulSoup(email['Html-part'], features="html.parser")
        assert not html.select('div.user_offerer strong.validation a')
        assert html.select('div.user_offerer h2')[0].text == 'Rattachement :'


    @mocked_mail
    @clean_database
    def test_validation_email_object_does_not_include_validation_link_if_offerer_is_already_validated(app):
        # Given
        validation_token = secrets.token_urlsafe(20)
        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=None)

        user = create_user(can_book_free_offers=False, departement_code='75', email='user@accenture.com',
                           public_name='Test', validation_token=validation_token)

        user_offerer = create_user_offerer(user=user, offerer=offerer, validation_token=validation_token)

        # When
        email = make_validation_email_object(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

        # Then
        html = BeautifulSoup(email['Html-part'], features="html.parser")
        assert not html.select('div.offerer strong.validation a')
        assert html.select('div.offerer h2')[0].text == 'Structure :'


    @mocked_mail
    @clean_database
    def test_validation_email_should_neither_return_clearTextPassword_nor_totallysafepsswd(app):
        # Given
        validation_token = secrets.token_urlsafe(20)
        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=validation_token)

        user = create_user(can_book_free_offers=False, departement_code='75', email='user@accenture.com',
                           public_name='Test', validation_token=validation_token)

        user_offerer = create_user_offerer(user=user, offerer=offerer, validation_token=validation_token)

        mocked_api_entreprises = get_mocked_response_status_200

        # When
        email = make_validation_email_object(offerer, user_offerer, get_by_siren=mocked_api_entreprises)

        # Then
        email_html_soup = BeautifulSoup(email['Html-part'], features="html.parser")
        assert 'clearTextPassword' not in str(email_html_soup)
        assert 'totallysafepsswd' not in str(email_html_soup)
