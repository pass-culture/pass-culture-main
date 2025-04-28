import datetime
import random
import string
from unittest.mock import patch

import pytest

from pcapi import settings as pcapi_settings
from pcapi.connectors import typeform
from pcapi.core.chronicles import api
from pcapi.core.chronicles import constants
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.chronicles import models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db


def random_string(length: int = 20) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


@pytest.mark.usefixtures("db_session")
class AnonymizeUnlinkedChronicleTest:
    def test_anonymize_old_chronicle(self):
        chronicle = chronicles_factories.ChronicleFactory(
            email="personalemail@example.com",
            dateCreated=datetime.date.today() - datetime.timedelta(days=750),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == "anonymized_email@anonymized.passculture"

    def test_do_not_anonymize_new_chronicle(self):
        email = "personalemail@example.com"
        chronicle = chronicles_factories.ChronicleFactory(
            email=email,
            dateCreated=datetime.date.today() - datetime.timedelta(days=700),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == email

    def test_do_not_anonymize_chronicle_linked_to_user(self):
        email = "personalemail@example.com"
        chronicle = chronicles_factories.ChronicleFactory(
            user=users_factories.BeneficiaryFactory(),
            email=email,
            dateCreated=datetime.date.today() - datetime.timedelta(days=750),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == email


@pytest.mark.usefixtures("db_session")
class ImportBookClubChroniclesTest:
    def _get_api_result(self):
        return [
            typeform.TypeformResponse(
                response_id=random_string(),
                date_submitted=datetime.datetime(2024, 10, 24),
                phone_number=None,
                email="email@mail.test",
                answers=[
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.AGE_ID.value,
                        choice_id=None,
                        text="18",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.CITY_ID.value,
                        choice_id=None,
                        text="Paris",
                    ),
                    typeform.TypeformAnswer(
                        field_id=random_string(),
                        choice_id=None,
                        text="should be ignored",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.NAME_ID.value,
                        choice_id=None,
                        text="Bob",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.BOOK_EAN_ID.value,
                        choice_id=random_string(),
                        text="1235467890123",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.CHRONICLE_ID.value,
                        choice_id=None,
                        text=random_string(150),
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value,
                        choice_id=constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value,
                        text="oui",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.BookClub.SOCIAL_MEDIA_QUESTION_ID.value,
                        choice_id=constants.BookClub.SOCIAL_MEDIA_ANSWER_ID.value,
                        text="oui",
                    ),
                ],
            ),
        ]

    def test_import_book_club_chronicles_with_old_chronicle(self):
        old_chronicle = chronicles_factories.ChronicleFactory()
        api_results = self._get_api_result()

        with patch("pcapi.core.chronicles.api.typeform.get_responses", return_value=api_results) as typeform_mock:
            api.import_book_club_chronicles()

            typeform_mock.assert_called_once_with(
                form_id=constants.BookClub.FORM_ID.value,
                num_results=pcapi_settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=old_chronicle.dateCreated,
                sort="submitted_at,asc",
            )

        chronicle = db.session.query(models.Chronicle).order_by(models.Chronicle.id.desc()).first()
        assert chronicle.email == "email@mail.test"

    def test_import_book_club_chronicles_without_old_chronicle(self):
        api_results = self._get_api_result()

        with patch("pcapi.core.chronicles.api.typeform.get_responses", return_value=api_results) as typeform_mock:
            api.import_book_club_chronicles()

            typeform_mock.assert_called_once_with(
                form_id=constants.BookClub.FORM_ID.value,
                num_results=pcapi_settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=None,
                sort="submitted_at,asc",
            )

        chronicle = db.session.query(models.Chronicle).order_by(models.Chronicle.id.desc()).first()
        assert chronicle.email == "email@mail.test"


@pytest.mark.usefixtures("db_session")
class SaveBookClubChronicleTest:
    def test_save_book_club_chronicle_full(self):
        ean = "1234567890123"
        ean_choice_id = random_string()
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.AGE_ID.value,
                    choice_id=None,
                    text="18",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CITY_ID.value,
                    choice_id=None,
                    text="Paris",
                ),
                typeform.TypeformAnswer(
                    field_id=random_string(),
                    choice_id=None,
                    text="should be ignored",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.NAME_ID.value,
                    choice_id=None,
                    text="Bob",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=ean_choice_id,
                    text=ean,
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value,
                    choice_id=constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value,
                    text="oui",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.SOCIAL_MEDIA_QUESTION_ID.value,
                    choice_id=constants.BookClub.SOCIAL_MEDIA_ANSWER_ID.value,
                    text="oui",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.age == 18
        assert chronicle.city == "Paris"
        assert chronicle.firstName == "Bob"
        assert chronicle.ean == ean
        assert chronicle.eanChoiceId == ean_choice_id
        assert chronicle.content == "some random chronicle description"
        assert chronicle.isIdentityDiffusible
        assert chronicle.isSocialMediaDiffusible
        assert not chronicle.isActive
        assert chronicle.externalId == form.response_id
        assert chronicle.userId is None

    def test_save_book_club_chronicle_empty(self):
        ean = "1234567890123"
        ean_choice_id = random_string()
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=ean_choice_id,
                    text=ean,
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.age is None
        assert chronicle.city is None
        assert chronicle.firstName is None
        assert chronicle.ean == ean
        assert chronicle.eanChoiceId == ean_choice_id
        assert chronicle.content == "some random chronicle description"
        assert not chronicle.isIdentityDiffusible
        assert not chronicle.isSocialMediaDiffusible
        assert not chronicle.isActive
        assert chronicle.externalId == form.response_id
        assert chronicle.userId is None

    def test_do_not_save_book_club_chronicle_without_email(self):
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email=None,
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_book_club_chronicle_without_content(self):
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_book_club_chronicle_without_ean(self):
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_book_club_chronicle_link_to_user(self):
        user = users_factories.UserFactory(
            email="email@mail.test",
        )
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.userId == user.id

    def test_save_book_club_chronicle_refuse_publication(self):
        users_factories.UserFactory(
            email="email@mail.test",
        )
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value,
                    choice_id=random_string(),
                    text="non",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.SOCIAL_MEDIA_QUESTION_ID.value,
                    choice_id=random_string(),
                    text="non",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicle = db.session.query(models.Chronicle).first()

        assert not chronicle.isIdentityDiffusible
        assert not chronicle.isSocialMediaDiffusible

    def test_save_book_club_chronicle_link_to_product(self):
        product = offers_factories.ProductFactory(
            ean="1234567890123",
        )
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicle = db.session.query(models.Chronicle).first()

        assert chronicle.products == [product]

    def test_save_book_club_chronicle_already_saved(self):
        old_chronicle = chronicles_factories.ChronicleFactory()
        ean = "1234567890123"
        ean_choice_id = random_string()
        form = typeform.TypeformResponse(
            response_id=old_chronicle.externalId,
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.BOOK_EAN_ID.value,
                    choice_id=ean_choice_id,
                    text=ean,
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_book_club_chronicle(form)

        chronicles = db.session.query(models.Chronicle).all()
        assert len(chronicles) == 1
        assert chronicles[0].id == old_chronicle.id


@pytest.mark.usefixtures("db_session")
class ExtractBookClubEanTest:
    def test_ean_in_text(self):
        ean = "1234567890123"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.BOOK_EAN_ID.value,
            choice_id=choice_id,
            text=f"book title - {ean} - december",
        )

        result = api._extract_book_club_ean(form)

        assert result == ean

    def test_choice_in_db(self):
        ean = "1234567890123"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.BOOK_EAN_ID.value,
            choice_id=choice_id,
            text="nothing to see here",
        )
        chronicles_factories.ChronicleFactory(ean=ean, eanChoiceId=choice_id)

        result = api._extract_book_club_ean(form)

        assert result == ean

    def test_ends_with_ean(self):
        ean = "1234567890123"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.BOOK_EAN_ID.value,
            choice_id=choice_id,
            text=f"book title - {ean}",
        )

        result = api._extract_book_club_ean(form)

        assert result == ean

    def test_unknown_choice(self):
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.BOOK_EAN_ID.value,
            choice_id=random_string(),
            text="nothing to see here",
        )

        result = api._extract_book_club_ean(form)

        assert result is None

    def test_empty_answer(self):
        form = typeform.TypeformAnswer(field_id="")

        result = api._extract_book_club_ean(form)

        assert result is None
