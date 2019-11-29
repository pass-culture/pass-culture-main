from bs4 import BeautifulSoup
from freezegun import freeze_time

from models import User
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_beneficiaries_import_email


@freeze_time('2019-05-20 12:00:00')
class MakeBeneficiariesImportEmailTest:
    def test_sends_date_in_subject(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        assert email["FromEmail"] == 'dev@passculture.app'
        assert email["FromName"] == 'pass Culture'
        assert email["Subject"] == 'Import des utilisateurs depuis Démarches Simplifiées 2019-05-20'

    def test_sends_number_of_newly_created_beneficiaries(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert parsed_email.find("p", {"id": 'total'}).text == "Nombre total d'utilisateurs créés : 2"

    def test_sends_list_of_import_errors(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert parsed_email.find("p", {"id": 'errors'}).text.strip() == "erreur import 1 erreur import 2"
