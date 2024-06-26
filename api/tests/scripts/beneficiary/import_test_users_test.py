import datetime
import io
import logging

from dateutil.relativedelta import relativedelta
import pytest

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.scripts.beneficiary import import_test_users
from pcapi.utils import crypto


AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=18, months=4)
AGE17_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=17, months=4)

CSV = f"""Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance,Role,SIREN,Mot de passe,Type
Doux,Jeanne,jeanne.doux@example.com,0102030405,86,86140,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,,interne:test
Smisse,Jean,jean.smisse@example.com,0102030406,44,44000,{AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},BENEFICIARY,,,interne:test
Vienne,Jeune17,jeune17.vienne@example.com,0102030407,44,44000,{AGE17_ELIGIBLE_BIRTH_DATE:%Y-%m-%d},UNDERAGE_BENEFICIARY,,,interne:test
Pro,Pierre,pro@example.com,0123456789,06,06000,2000-01-01,PRO,11122233,PierrePro$123,interne:test
"""

BOUNTY_EMAIL = "unit-test-bùg-bounty-hunter-0123456789abcdef@bugbounty.ninja"
BOUNTY_FIRST_NAME = "Hackèrman"
BOUNTY_CSV = f"""Nom,Prénom,Mail,Téléphone,Département,Code postal,Date de naissance,Role,SIREN,Mot de passe,Type
Doux,{BOUNTY_FIRST_NAME},{BOUNTY_EMAIL},0102030405,86,86140,2000-01-01,PRO,10000135,,externe:bug-bounty
Dur,Hubert,touriste@mars.org,0102030405,86,86140,2000-01-01,PRO,10000115,,interne:test
Dur,{BOUNTY_FIRST_NAME},another_hunter@bugbounty.ninja,0102030405,86,86140,2000-01-01,PRO,10000105,,externe:bug-bounty
"""


@pytest.mark.usefixtures("db_session")
class ReadFileTest:
    @pytest.mark.parametrize("update_if_exists", [True, False])
    def test_read_file(self, update_if_exists, caplog):
        jean = users_factories.BeneficiaryGrant18Factory(email="jean.smisse@example.com", lastName="Old name")
        assert len(jean.deposits) == 1

        csv_file = io.StringIO(CSV)
        with caplog.at_level(logging.INFO):
            users = import_test_users.create_users_from_csv(csv_file, update_if_exists=update_if_exists)

        assert "jea***@example.com" in caplog.messages[1]
        if update_if_exists:
            assert "jea***@example.com" in caplog.messages[2]
            assert "jeu***@example.com" in caplog.messages[5]
            assert "p***@example.com" in caplog.messages[10]

        if update_if_exists:
            assert len(users) == 4
            jeanne, jean, jeune17, pierre = users  # pylint: disable=unbalanced-tuple-unpacking
        else:
            jeanne, jeune17, pierre = users  # pylint: disable=unbalanced-tuple-unpacking
            jean = None

        assert jeanne.firstName == "Jeanne"
        assert jeanne.lastName == "Doux"
        assert jeanne.dateOfBirth.date() == AGE18_ELIGIBLE_BIRTH_DATE.date()
        assert jeanne.email == "jeanne.doux@example.com"
        assert jeanne.phoneNumber == "+33102030405"
        assert jeanne.departementCode == "86"
        assert jeanne.postalCode == "86140"
        assert jeanne.comment == "interne:test"
        assert jeanne.isEmailValidated
        assert jeanne.has_beneficiary_role
        assert jeanne.has_test_role
        assert len(jeanne.deposits) == 1

        assert jeanne.checkPassword(settings.TEST_DEFAULT_PASSWORD)

        if update_if_exists:
            assert jean.lastName == "Smisse"
            assert len(jean.deposits) == 1

        assert jeune17.firstName == "Jeune17"
        assert jeune17.has_underage_beneficiary_role

        assert pierre.firstName == "Pierre"
        assert pierre.lastName == "Pro"
        assert pierre.email == "pro@example.com"
        assert pierre.phoneNumber == "+33123456789"
        assert pierre.departementCode == "06"
        assert pierre.postalCode == "06000"
        assert pierre.comment == "interne:test"
        assert pierre.isEmailValidated
        assert pierre.has_pro_role
        assert not pierre.has_beneficiary_role
        assert pierre.has_test_role
        assert len(pierre.deposits) == 0

        offerer = offerers_models.Offerer.query.one()
        assert offerer.siren == "111222337"
        assert offerer.name == "Structure Pro"
        assert offerer.postalCode == "06000"
        assert offerer.city == "MA VILLE"
        assert offerer.isValidated

        venue = offerers_models.Venue.query.filter_by(name="Lieu Pro").one()
        assert venue.siret == "11122233700011"
        assert venue.postalCode == "06000"
        assert venue.city == "MA VILLE"
        assert venue.managingOfferer == offerer

        digital_venue = offerers_models.Venue.query.filter_by(name="Offre numérique").one()
        assert digital_venue.siret is None
        assert digital_venue.managingOfferer == offerer

        bank_accounts = finance_models.BankAccount.query.order_by(finance_models.BankAccount.id).all()
        for bank_account, status in zip(bank_accounts, finance_models.BankAccountApplicationStatus):
            assert bank_account.offerer == offerer
            assert bank_account.status == status
            if status is finance_models.BankAccountApplicationStatus.ACCEPTED:
                assert len(bank_account.venueLinks) == 1
                assert bank_account.venueLinks[0].venue == venue
            else:
                assert not bank_account.venueLinks

        assert pierre.checkPassword("PierrePro$123")

        admin = User.query.filter_by(email="admin@example.com").one()
        assert admin.has_admin_role
        assert not admin.has_beneficiary_role
        assert not admin.has_test_role

    def test_create_provider_for_bounty_users(self, client):
        csv_file = io.StringIO(BOUNTY_CSV)
        import_test_users.create_users_from_csv(csv_file)

        prefix = f"staging_{BOUNTY_EMAIL}"
        api_key = offerers_models.ApiKey.query.filter_by(prefix=prefix).one()
        assert crypto.hash_public_api_key(BOUNTY_EMAIL) == api_key.secret

        # This call ensures that we have access to the api and at least one venue
        # attached to this provider
        client = client.with_explicit_token(f"{prefix}_{BOUNTY_EMAIL}")
        response = client.get("/public/offers/v1/offerer_venues")
        assert response.status_code == 200
        assert len(response.json) == 1
