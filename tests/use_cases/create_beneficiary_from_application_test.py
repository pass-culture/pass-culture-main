from datetime import datetime
from unittest.mock import patch, MagicMock

from freezegun import freeze_time
from tests.conftest import clean_database

from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from models import BeneficiaryImport, UserSQLEntity
from models.beneficiary_import_status import ImportStatus
from models.deposit import Deposit
from use_cases.create_beneficiary_from_application import \
    CreateBeneficiaryFromApplication
from repository import repository
from tests.model_creators.generic_creators import create_user
from tests.domain_creators.generic_creators import create_domain_beneficiary_pre_subcription


@patch('use_cases.create_beneficiary_from_application.send_raw_email')
@patch('use_cases.create_beneficiary_from_application.send_activation_email')
@patch('domain.password.random_token')
@patch('infrastructure.repository.beneficiary.beneficiary_pre_subscription_sql_converter.random_password')
@freeze_time('2020-10-15 09:00:00')
@clean_database
def test_saved_a_beneficiary_from_application(stubed_random_password,
                                              stubed_random_token,
                                              mocked_send_activation_email,
                                              stubed_send_raw_email,
                                              app):
    # Given
    application_id = 7
    stubed_random_password.return_value = b'random-password'
    stubed_random_token.return_value = 'token'
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(
        activity='Apprenti',
        address='3 rue de Valois',
        application_id=application_id,
        city='Paris',
        civility='Mme',
        date_of_birth=datetime(1995, 2, 5),
        email='rennes@example.org',
        first_name='Thomas',
        last_name='DURAND',
        phone_number='0123456789',
        postal_code='35123',
        source='jouve',
        source_id=None,
    )

    beneficiary_jouve_repository = MagicMock()
    beneficiary_jouve_repository.get_application_by.return_value = beneficiary_pre_subscription
    create_beneficiary_from_application = CreateBeneficiaryFromApplication(
        beneficiary_jouve_repository=beneficiary_jouve_repository,
        beneficiary_sql_repository=BeneficiarySQLRepository()
    )

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    beneficiary = UserSQLEntity.query.one()
    assert beneficiary.activity == 'Apprenti'
    assert beneficiary.address == '3 rue de Valois'
    assert beneficiary.canBookFreeOffers == True
    assert beneficiary.city == 'Paris'
    assert beneficiary.civility == 'Mme'
    assert beneficiary.dateOfBirth == datetime(1995, 2, 5)
    assert beneficiary.departementCode == '35'
    assert beneficiary.email == 'rennes@example.org'
    assert beneficiary.firstName == 'Thomas'
    assert beneficiary.hasSeenTutorials == False
    assert beneficiary.isAdmin == False
    assert beneficiary.lastName == 'DURAND'
    assert beneficiary.password == b'random-password'
    assert beneficiary.phoneNumber == '0123456789'
    assert beneficiary.postalCode == '35123'
    assert beneficiary.publicName == 'Thomas DURAND'
    assert beneficiary.resetPasswordToken == 'token'
    assert beneficiary.resetPasswordTokenValidityLimit == datetime(2020, 11, 14, 9)

    deposit = Deposit.query.one()
    assert deposit.amount == 500
    assert deposit.source == 'dossier jouve [7]'
    assert deposit.userId == beneficiary.id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.CREATED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == beneficiary

    mocked_send_activation_email.assert_called_once_with(user=beneficiary, send_email=stubed_send_raw_email)


@clean_database
def test_cannot_save_beneficiary_if_email_is_already_taken(app):
    # Given
    email = 'rennes@example.org'

    user = create_user(email=email, idx=4)
    repository.save(user)

    application_id = 7
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(
        date_of_birth=datetime(1995, 2, 5),
        application_id=application_id,
        email=email,
    )
    beneficiary_jouve_repository = MagicMock()
    beneficiary_jouve_repository.get_application_by.return_value = beneficiary_pre_subscription
    create_beneficiary_from_application = CreateBeneficiaryFromApplication(
        beneficiary_jouve_repository=beneficiary_jouve_repository,
        beneficiary_sql_repository=BeneficiarySQLRepository()
    )

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    user = UserSQLEntity.query.one()
    assert user.id == 4

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == None
    assert beneficiary_import.detail == f"Email {email} is already taken."


@clean_database
def test_cannot_save_beneficiary_if_duplicate(app):
    # Given
    first_name = 'Thomas'
    last_name = 'DURAND'
    date_of_birth = datetime(1995, 2, 5)
    existing_user_id = 4

    user = create_user(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, idx=existing_user_id)
    repository.save(user)

    application_id = 7
    beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription(
        date_of_birth=date_of_birth,
        application_id=application_id,
        first_name=first_name,
        last_name=last_name,
    )
    beneficiary_jouve_repository = MagicMock()
    beneficiary_jouve_repository.get_application_by.return_value = beneficiary_pre_subscription
    create_beneficiary_from_application = CreateBeneficiaryFromApplication(
        beneficiary_jouve_repository=beneficiary_jouve_repository,
        beneficiary_sql_repository=BeneficiarySQLRepository()
    )

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    user = UserSQLEntity.query.one()
    assert user.id == existing_user_id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == None
    assert beneficiary_import.detail == f"User with id {existing_user_id} is a duplicate."
