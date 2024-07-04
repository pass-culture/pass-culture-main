from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import json
from zipfile import ZipFile

import pytest

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import enum as finance_enum
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.tasks import gdpr_tasks
from pcapi.tasks.serialization import gdpr_tasks as serializers

from tests.test_utils import StorageFolderManager


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


def generate_beneficiary(now: datetime | None = None) -> serializers.DataContainer:
    now = now or datetime(2024, 1, 1)
    user = users_factories.UserFactory(
        activity="Lycéen",
        address="123 rue du pass",
        civility="M.",
        city="Paris",
        culturalSurveyFilledDate=now,
        departementCode="75",
        dateCreated=now,
        dateOfBirth=datetime(2010, 1, 1),
        email="valid_email@example.com",
        firstName="Beneficiary",
        isActive=True,
        isEmailValidated=True,
        lastName="bénéficiaire",
        married_name="married_name",
        postalCode="75000",
        schoolType=users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
        validatedBirthDate=date(2010, 1, 1),
        notificationSubscriptions={
            "marketing_email": True,
            "marketing_push": False,
        },
        roles=[users_models.UserRole.BENEFICIARY],
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now - timedelta(days=2),
        deviceId="anotsorandomdeviceid2",
        location="Lyon",
        source="phone1",
        os="oldOs",
        user=user,
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now,
        deviceId="anotsorandomdeviceid",
        location="Paris",
        source="phone 2",
        os="os/2",
        user=user,
    )
    users_factories.EmailUpdateEntryFactory(
        creationDate=now - timedelta(days=2),
        newUserEmail="intermediary",
        newDomainEmail="example.com",
        oldUserEmail="old",
        oldDomainEmail="example.com",
        user=user,
    )
    users_factories.EmailUpdateEntryFactory(
        creationDate=now,
        newUserEmail="beneficiary",
        newDomainEmail="example.com",
        oldUserEmail="intermediary",
        oldDomainEmail="example.com",
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now - timedelta(days=2),
        actionType=history_models.ActionType.USER_SUSPENDED,
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now,
        actionType=history_models.ActionType.USER_UNSUSPENDED,
        user=user,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        dateCreated=now,
        eligibilityType=users_models.EligibilityType.AGE18,
        status=fraud_models.FraudCheckStatus.OK,
        type=fraud_models.FraudCheckType.DMS,
        updatedAt=now + timedelta(days=1),
        user=user,
    )
    users_factories.DepositGrantFactory(
        user=user,
        dateCreated=now - timedelta(days=2),
        dateUpdated=now + timedelta(days=1),
        expirationDate=now + timedelta(days=15000),
        amount=Decimal("300.0"),
        source="source",
        type=finance_enum.DepositType.GRANT_18,
    )
    bookings_factories.BookingFactory(
        user=user,
        dateCreated=now,
        dateUsed=now,
        quantity=1,
        amount=Decimal("10.00"),
        status=bookings_models.BookingStatus.CONFIRMED,
        stock__offer__name="offer_name",
        stock__offer__venue__name="venue_name",
        stock__offer__venue__managingOfferer__name="offerer_name",
    )
    bookings_factories.BookingFactory(
        user=user,
        cancellationDate=now,
        dateCreated=now,
        quantity=1,
        amount=Decimal("50.00"),
        status=bookings_models.BookingStatus.CANCELLED,
        stock__offer__name="offer2_name",
        stock__offer__venue__name="venue2_name",
        stock__offer__venue__managingOfferer__name="offerer2_name",
    )
    return user


class GetUpdateExtractTest:
    def test_nominal(self) -> None:
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        extract_id = extract.id

        with assert_num_queries(1):
            result = gdpr_tasks._get_and_update_extract(extract_id)

        db.session.flush()
        assert result is extract

    def test_wrong_extract_id(self) -> None:
        with assert_num_queries(1):
            with pytest.raises(gdpr_tasks.ExtractNotFound):
                gdpr_tasks._get_and_update_extract(0)

    def test_processed_extract(self) -> None:
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.utcnow(),
        )
        extract_id = extract.id

        with assert_num_queries(1):
            with pytest.raises(gdpr_tasks.ExtractNotFound):
                gdpr_tasks._get_and_update_extract(extract_id)

    def test_expired_extract(self) -> None:
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.utcnow() - timedelta(days=8),
        )
        extract_id = extract.id

        with assert_num_queries(1):
            with pytest.raises(gdpr_tasks.ExtractNotFound):
                gdpr_tasks._get_and_update_extract(extract_id)

    def test_inactive_admin(self) -> None:
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            authorUser__isActive=False,
        )
        extract_id = extract.id

        with assert_num_queries(1):
            with pytest.raises(gdpr_tasks.ExtractNotPermitted):
                gdpr_tasks._get_and_update_extract(extract_id)

    def test_beneficiary_author(self) -> None:
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            authorUser=users_factories.BeneficiaryFactory(),
        )
        extract_id = extract.id

        with assert_num_queries(1):
            with pytest.raises(gdpr_tasks.ExtractNotPermitted):
                gdpr_tasks._get_and_update_extract(extract_id)


class ExtractBeneficiaryDataTest(StorageFolderManager):
    # 1 extract + user + admin
    # 2 login device history
    # 3 user_email_history
    # 4 action_history
    # 5 beneficiary_fraud_check
    # 6 deposit
    # 7 bookings
    # 8 update GdprUserExtract
    # 9 generate action history
    expected_queries = 9
    # 1 json
    output_files_count = 1
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_json_output(self) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)
        with assert_num_queries(self.expected_queries):
            gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"

        json_file_name = f"{user.firstName}_{user.lastName}.json"
        with ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert json_file_name in files
            with zip_pointer.open(json_file_name) as json_pointer:
                raw_data = json_pointer.read()
                json_data = raw_data.decode("utf-8")
                result = json.loads(json_data)

        assert "generationDate" in result
        del result["generationDate"]
        assert result == {
            "internal": {
                "user": {
                    "activity": "Lycéen",
                    "address": "123 rue du pass",
                    "civility": "M.",
                    "city": "Paris",
                    "culturalSurveyFilledDate": "2024-01-01T00:00:00",
                    "departementCode": "75",
                    "dateCreated": "2024-01-01T00:00:00",
                    "dateOfBirth": "2010-01-01T00:00:00",
                    "email": "valid_email@example.com",
                    "firstName": "Beneficiary",
                    "isActive": True,
                    "isEmailValidated": True,
                    "lastName": "bénéficiaire",
                    "marriedName": "married_name",
                    "postalCode": "75000",
                    "schoolType": "Collège public",
                    "validatedBirthDate": "2010-01-01",
                },
                "marketing": {"marketingEmails": True, "marketingNotifications": False},
                "loginDevices": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "deviceId": "anotsorandomdeviceid2",
                        "location": "Lyon",
                        "source": "phone1",
                        "os": "oldOs",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "deviceId": "anotsorandomdeviceid",
                        "location": "Paris",
                        "source": "phone 2",
                        "os": "os/2",
                    },
                ],
                "emailsHistory": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "newEmail": "intermediary@example.com",
                        "oldEmail": "old@example.com",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "newEmail": "beneficiary@example.com",
                        "oldEmail": "intermediary@example.com",
                    },
                ],
                "actionsHistory": [
                    {"actionDate": "2023-12-30T00:00:00", "actionType": "Compte suspendu"},
                    {"actionDate": "2024-01-01T00:00:00", "actionType": "Compte réactivé"},
                ],
                "beneficiaryValidations": [
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "eligibilityType": "age-18",
                        "status": "ok",
                        "type": "dms",
                        "updatedAt": "2024-01-02T00:00:00",
                    }
                ],
                "deposits": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "dateUpdated": "2024-01-02T00:00:00",
                        "expirationDate": "2065-01-25T00:00:00",
                        "amount": 300.0,
                        "source": "source",
                        "type": "GRANT_18",
                    }
                ],
                "bookings": [
                    {
                        "cancellationDate": None,
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": "2024-01-01T00:00:00",
                        "quantity": 1,
                        "amount": 10.0,
                        "status": "CONFIRMED",
                        "name": "offer_name",
                        "venue": "venue_name",
                        "offerer": "offerer_name",
                    },
                    {
                        "cancellationDate": "2024-01-01T00:00:00",
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": None,
                        "quantity": 1,
                        "amount": 50.0,
                        "status": "CANCELLED",
                        "name": "offer2_name",
                        "venue": "venue2_name",
                        "offerer": "offerer2_name",
                    },
                ],
            },
            "external": {
                "brevo": {
                    "email": "valid_email@example.com",
                    "id": 42,
                    "emailBlacklisted": False,
                    "smsBlacklisted": False,
                    "createdAt": "2017-05-02T16:40:31Z",
                    "modifiedAt": "2017-05-02T16:40:31Z",
                    "attributes": {
                        "FIRST_NAME": "valid",
                        "LAST_NAME": "email",
                        "SMS": "3087433387669",
                        "CIV": "1",
                        "DOB": "1986-04-13",
                        "ADDRESS": "987 5th avenue",
                        "ZIP_CODE": "87544",
                        "CITY": "New-York",
                        "AREA": "NY",
                    },
                    "listIds": [40],
                    "statistics": {
                        "messagesSent": [
                            {"campaignId": 21, "eventTime": "2016-05-03T20:15:13Z"},
                            {"campaignId": 42, "eventTime": "2016-10-17T10:30:01Z"},
                        ],
                        "opened": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"},
                            {"campaignId": 68, "count": 1, "eventTime": "2017-01-30T13:56:40Z", "ip": "66.249.93.217"},
                        ],
                        "clicked": [
                            {
                                "campaignId": 21,
                                "links": [
                                    {
                                        "count": 2,
                                        "eventTime": "2016-05-03T21:25:01Z",
                                        "ip": "66.249.93.118",
                                        "url": "https://url.domain.com/fbe5387ec717e333628380454f68670010b205ff/1/go?uid={EMAIL}&utm_source=brevo&utm_campaign=test_camp&utm_medium=email",
                                    }
                                ],
                            }
                        ],
                        "delivered": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"}
                        ],
                    },
                }
            },
        }
