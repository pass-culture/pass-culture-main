from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import json
from unittest import mock
from zipfile import ZipFile

import pytest

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import enum as finance_enum
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offers import factories as offers_factories
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


def generate_beneficiary() -> serializers.DataContainer:
    now = datetime(2024, 1, 1)
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
    users_factories.EmailConfirmationEntryFactory(
        creationDate=now - timedelta(days=2),
        newUserEmail="intermediary",
        newDomainEmail="example.com",
        oldUserEmail="old",
        oldDomainEmail="example.com",
        user=user,
    )
    users_factories.EmailAdminValidationEntryFactory(
        eventType=users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
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


def generate_minimal_beneficiary():
    # generate a user with all objects where all optional fields to None
    now = datetime(2024, 1, 1)
    user = users_models.User(
        dateCreated=now,
        email="empty@example.com",
        hasSeenProTutorials=False,
        hasSeenProRgs=False,
        needsToFillCulturalSurvey=False,
        notificationSubscriptions=None,
        roles=[users_models.UserRole.BENEFICIARY],
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(
        users_models.LoginDeviceHistory(
            user=user,
            deviceId="a device id",
            dateCreated=now,
        )
    )
    db.session.add(
        users_models.UserEmailHistory(
            user=user,
            oldUserEmail="oldUserEmail",
            oldDomainEmail="example.com",
            creationDate=now,
            eventType=users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
        )
    )
    db.session.add(
        history_models.ActionHistory(
            user=user,
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now,
        )
    )
    db.session.add(
        fraud_models.BeneficiaryFraudCheck(
            user=user,
            dateCreated=now,
            thirdPartyId="third_party_id",
            type=fraud_models.FraudCheckType.DMS,
            updatedAt=now,
        )
    )
    deposit = finance_models.Deposit(
        user=user,
        amount=Decimal("300.00"),
        source="démarches simplifiées dossier [1234567]",
        dateCreated=now,
        version=1,
        type=finance_enum.DepositType.GRANT_18,
    )
    db.session.add(deposit)
    stock = offers_factories.StockFactory(
        offer__name="offer_name",
        offer__venue__name="venue_name",
        offer__venue__managingOfferer__name="offerer_name",
    )
    db.session.add(
        bookings_models.Booking(
            user=user,
            dateCreated=now,
            stock=stock,
            venue=stock.offer.venue,
            offerer=stock.offer.venue.managingOfferer,
            quantity=1,
            token="token",
            amount=Decimal("13.34"),
            status=bookings_models.BookingStatus.CANCELLED,
            cancellationDate=now,
            deposit=deposit,
        )
    )
    db.session.flush()
    db.session.refresh(user)
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
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
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
    # 2 pdf
    output_files_count = 2

    @mock.patch("pcapi.tasks.gdpr_tasks.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_json_output(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)
        with assert_num_queries(self.expected_queries):
            gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"

        json_file_name = f"{user.email}.json"
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
            "external": {
                "brevo": {
                    "attributes": {
                        "ADDRESS": "987 5th avenue",
                        "AREA": "NY",
                        "CITY": "New-York",
                        "CIV": "1",
                        "DOB": "1986-04-13",
                        "FIRST_NAME": "valid",
                        "LAST_NAME": "email",
                        "SMS": "3087433387669",
                        "ZIP_CODE": "87544",
                    },
                    "createdAt": "2017-05-02T16:40:31Z",
                    "email": "valid_email@example.com",
                    "emailBlacklisted": False,
                    "id": 42,
                    "listIds": [40],
                    "modifiedAt": "2017-05-02T16:40:31Z",
                    "smsBlacklisted": False,
                    "statistics": {
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
                        "messagesSent": [
                            {"campaignId": 21, "eventTime": "2016-05-03T20:15:13Z"},
                            {"campaignId": 42, "eventTime": "2016-10-17T10:30:01Z"},
                        ],
                        "opened": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"},
                            {"campaignId": 68, "count": 1, "eventTime": "2017-01-30T13:56:40Z", "ip": "66.249.93.217"},
                        ],
                    },
                }
            },
            "internal": {
                "actionsHistory": [
                    {"actionDate": "2023-12-30T00:00:00", "actionType": "Compte suspendu"},
                    {"actionDate": "2024-01-01T00:00:00", "actionType": "Compte réactivé"},
                ],
                "beneficiaryValidations": [
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "eligibilityType": "Pass 18",
                        "status": "Succès",
                        "type": "Démarches simplifiées",
                        "updatedAt": "2024-01-02T00:00:00",
                    }
                ],
                "bookings": [
                    {
                        "amount": 10.0,
                        "cancellationDate": None,
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": "2024-01-01T00:00:00",
                        "name": "offer_name",
                        "offerer": "offerer_name",
                        "quantity": 1,
                        "status": "Réservé",
                        "venue": "venue_name",
                    },
                    {
                        "amount": 50.0,
                        "cancellationDate": "2024-01-01T00:00:00",
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": None,
                        "name": "offer2_name",
                        "offerer": "offerer2_name",
                        "quantity": 1,
                        "status": "Annulé",
                        "venue": "venue2_name",
                    },
                ],
                "deposits": [
                    {
                        "amount": 300.0,
                        "dateCreated": "2023-12-30T00:00:00",
                        "dateUpdated": "2024-01-02T00:00:00",
                        "expirationDate": "2065-01-25T00:00:00",
                        "source": "source",
                        "type": "Pass 18",
                    }
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
                "loginDevices": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "deviceId": "anotsorandomdeviceid2",
                        "location": "Lyon",
                        "os": "oldOs",
                        "source": "phone1",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "deviceId": "anotsorandomdeviceid",
                        "location": "Paris",
                        "os": "os/2",
                        "source": "phone 2",
                    },
                ],
                "marketing": {"marketingEmails": True, "marketingNotifications": False},
                "user": {
                    "activity": "Lycéen",
                    "address": "123 rue du pass",
                    "city": "Paris",
                    "civility": "M.",
                    "culturalSurveyFilledDate": "2024-01-01T00:00:00",
                    "dateCreated": "2024-01-01T00:00:00",
                    "dateOfBirth": "2010-01-01T00:00:00",
                    "departementCode": "75",
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
            },
        }

    @mock.patch("pcapi.tasks.gdpr_tasks.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_html(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)
        with assert_num_queries(self.expected_queries):
            gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d\'accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: none;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n            .underline {\n                text-decoration: underline;\n            }\n\n\n\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d\'accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d\'accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d\'informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>📱 <span class=underline>Données de l’utilisateur</span></h3>\n        <table class="borderless">\n            <tr><td>Nom</td><td>Beneficiary</td></tr>\n            <tr><td>Prénom</td><td>bénéficiaire</td></tr>\n            <tr><td>Nom de mariage</td><td>married_name</td></tr> \n            <tr><td>Adresse de messagerie</td><td>valid_email@example.com</td></tr>\n            <tr><td>Adresse</td><td>123 rue du pass</td></tr>\n            <tr><td>Code postal</td><td>75000</td></tr>\n            <tr><td>Ville</td><td>Paris</td></tr>\n            <tr><td>Département</td><td>75</td></tr>\n            <tr><td>Date de naissance</td><td>01/01/2010</td></tr> \n            <tr><td>Date de naissance confirmée</td><td>01/01/2010</td></tr>\n            <tr><td>Date de création du compte</td><td>01/01/2024 00:00:00</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            <tr><td>Activité</td><td>Lycéen</td></tr>\n            <tr><td>Type d\'école</td><td>Collège public</td></tr>\n        </table>\n\n        <h3>🎯 <span class=underline>Informations marketing</span></h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>oui</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>non</td></tr>\n        </table>\n\n        \n            <h3>🌐 <span class=underline>Historique des moyens de connexion</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Identifiant de l\'appareil</td><td>anotsorandomdeviceid2</td></tr>\n                    <tr><td>Type d\'appareil</td><td>phone1</td></tr>\n                    <tr><td>Système d\'exploitation</td><td>oldOs</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Identifiant de l\'appareil</td><td>anotsorandomdeviceid</td></tr>\n                    <tr><td>Type d\'appareil</td><td>phone 2</td></tr>\n                    <tr><td>Système d\'exploitation</td><td>os/2</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>📧 <span class=underline>Historique des changements d\'adresse de messagerie</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>old@example.com</td></tr>\n                    <tr><td>Nouvelle adresse email</td><td>intermediary@example.com</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>intermediary@example.com</td></tr>\n                    <tr><td>Nouvelle adresse email</td><td>beneficiary@example.com</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>⛔ <span class=underline>Historique des blocages du compte « pass Culture »</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte suspendu</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte réactivé</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>👌 <span class=underline>Validations d\'identité</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la validation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Moyen de la validation</td><td>Démarches simplifiées</td></tr>\n                    <tr><td>Résultat</td><td>Succès</td></tr>\n                     <tr><td>Dernière modification</td><td>02/01/2024 00:00:00</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>💰 <span class=underline>Crédits</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date d\'obtention</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Date d\'expiration</td><td>25/01/2065 00:00:00</td></tr>\n                    <tr><td>Valeur</td><td>300,00€</td></tr>\n                    <tr><td>Source</td><td>source</td></tr>\n                    <tr><td>Dernière modification</td><td>02/01/2024 00:00:00</td></tr>\n                    <tr><td>Type de crédit</td><td>Pass 18</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>📅 <span class=underline>Réservations effectuées depuis l’application « pass Culture »</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>10,00€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Date de retrait</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>État</td><td>Réservé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer_name</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer2_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>50,00€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Date d\'annulation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>État</td><td>Annulé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue2_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer2_name</td></tr>\n                </table>\n            \n        \n    <div class="purple-background">\n        💡 Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )

    def test_pdf_generated(self, css_font_http_request_mock):
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)

        gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"
        pdf_file_name = f"{user.email}.pdf"
        with ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read()

    @mock.patch("pcapi.tasks.gdpr_tasks.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_empty_user(self, pdf_generator_mock=None) -> None:
        user = users_models.User(
            firstName="firstname",
            lastName="lastName",
            email="firstname.lastname@example.com",
            dateCreated=datetime(2024, 6, 26, 13, 14, 28),
        )
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)
        with assert_num_queries(self.expected_queries):
            gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d\'accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: none;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n            .underline {\n                text-decoration: underline;\n            }\n\n\n\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d\'accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d\'accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d\'informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>📱 <span class=underline>Données de l’utilisateur</span></h3>\n        <table class="borderless">\n            <tr><td>Nom</td><td>firstname</td></tr>\n            <tr><td>Prénom</td><td>lastName</td></tr>\n            \n            <tr><td>Adresse de messagerie</td><td>firstname.lastname@example.com</td></tr>\n            \n            \n            \n            \n            \n            \n            <tr><td>Date de création du compte</td><td>26/06/2024 13:14:28</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            \n            \n        </table>\n\n        <h3>🎯 <span class=underline>Informations marketing</span></h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>oui</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>oui</td></tr>\n        </table>\n\n        \n\n        \n\n        \n\n        \n\n        \n\n        \n    <div class="purple-background">\n        💡 Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )

    @mock.patch("pcapi.tasks.gdpr_tasks.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_minimal_non_empty_user(self, pdf_generator_mock):
        user = generate_minimal_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        payload = serializers.ExtractBeneficiaryDataRequest(extract_id=extract.id)
        with assert_num_queries(self.expected_queries):
            gdpr_tasks.extract_beneficiary_data(payload)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d\'accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: none;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n            .underline {\n                text-decoration: underline;\n            }\n\n\n\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d\'accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d\'accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d\'informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>📱 <span class=underline>Données de l’utilisateur</span></h3>\n        <table class="borderless">\n            \n            \n            \n            <tr><td>Adresse de messagerie</td><td>empty@example.com</td></tr>\n            \n            \n            \n            \n            \n            \n            <tr><td>Date de création du compte</td><td>01/01/2024 00:00:00</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            \n            \n        </table>\n\n        <h3>🎯 <span class=underline>Informations marketing</span></h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>non</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>non</td></tr>\n        </table>\n\n        \n            <h3>🌐 <span class=underline>Historique des moyens de connexion</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Identifiant de l\'appareil</td><td>a device id</td></tr>\n                    \n                    \n                </table>\n            \n        \n\n        \n            <h3>📧 <span class=underline>Historique des changements d\'adresse de messagerie</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>oldUserEmail@example.com</td></tr>\n                    \n                </table>\n            \n        \n\n        \n            <h3>⛔ <span class=underline>Historique des blocages du compte « pass Culture »</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte suspendu</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>👌 <span class=underline>Validations d\'identité</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la validation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Moyen de la validation</td><td>Démarches simplifiées</td></tr>\n                    \n                     <tr><td>Dernière modification</td><td>01/01/2024 00:00:00</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>💰 <span class=underline>Crédits</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Date d\'obtention</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Valeur</td><td>300,00€</td></tr>\n                    <tr><td>Source</td><td>démarches simplifiées dossier [1234567]</td></tr>\n                    \n                    <tr><td>Type de crédit</td><td>Pass 18</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>📅 <span class=underline>Réservations effectuées depuis l’application « pass Culture »</span></h3>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>13,34€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Date d\'annulation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>État</td><td>Annulé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer_name</td></tr>\n                </table>\n            \n        \n    <div class="purple-background">\n        💡 Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )
