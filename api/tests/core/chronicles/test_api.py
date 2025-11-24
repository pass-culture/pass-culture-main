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
                        field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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
class SaveBookChroniclesTest:
    @pytest.mark.parametrize(
        "club_constants,club_type,product_identifier_type",
        [
            (constants.BookClub, models.ChronicleClubType.BOOK_CLUB, models.ChronicleProductIdentifierType.EAN),
            (constants.CineClub, models.ChronicleClubType.CINE_CLUB, models.ChronicleProductIdentifierType.ALLOCINE_ID),
            (constants.AlbumClub, models.ChronicleClubType.ALBUM_CLUB, models.ChronicleProductIdentifierType.EAN),
            (
                constants.ConcertClub,
                models.ChronicleClubType.CONCERT_CLUB,
                models.ChronicleProductIdentifierType.OFFER_ID,
            ),
        ],
    )
    def test_save_chronicle_full(self, club_constants, club_type, product_identifier_type):
        identifier = "1234567890123"
        identifier_choice_id = random_string()
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=random_string(),
                    choice_id=None,
                    text="should be ignored",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.NAME_ID.value,
                    choice_id=None,
                    text="Bob",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.PRODUCT_IDENTIFIER_FIELD_ID.value,
                    choice_id=identifier_choice_id,
                    text=f" title - {identifier}",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value,
                    choice_id=club_constants.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value,
                    text="oui",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.SOCIAL_MEDIA_QUESTION_ID.value,
                    choice_id=club_constants.SOCIAL_MEDIA_ANSWER_ID.value,
                    text="oui",
                ),
            ],
        )
        if hasattr(club_constants, "AGE_ID"):
            form.answers.append(
                typeform.TypeformAnswer(
                    field_id=club_constants.AGE_ID.value,
                    choice_id=None,
                    text="18",
                )
            )
        if hasattr(club_constants, "CITY_ID"):
            form.answers.append(
                typeform.TypeformAnswer(
                    field_id=club_constants.CITY_ID.value,
                    choice_id=None,
                    text="Paris",
                ),
            )

        api.save_chronicle(
            form=form,
            club_constants=club_constants,
            club_type=club_type,
            product_identifier_type=product_identifier_type,
        )

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.age == (18 if hasattr(club_constants, "AGE_ID") else None)
        assert chronicle.city == ("Paris" if hasattr(club_constants, "CITY_ID") else None)
        assert chronicle.firstName == "Bob"
        assert chronicle.productIdentifier == identifier
        assert chronicle.productIdentifierType == product_identifier_type
        assert chronicle.identifierChoiceId == identifier_choice_id
        assert chronicle.content == "some random chronicle description"
        assert chronicle.isIdentityDiffusible
        assert chronicle.isSocialMediaDiffusible
        assert not chronicle.isActive
        assert chronicle.externalId == form.response_id
        assert chronicle.userId is None
        assert chronicle.clubType == club_type

    @pytest.mark.parametrize(
        "club_constants,club_type,product_identifier_type",
        [
            (constants.BookClub, models.ChronicleClubType.BOOK_CLUB, models.ChronicleProductIdentifierType.EAN),
            (constants.CineClub, models.ChronicleClubType.CINE_CLUB, models.ChronicleProductIdentifierType.ALLOCINE_ID),
            (constants.AlbumClub, models.ChronicleClubType.ALBUM_CLUB, models.ChronicleProductIdentifierType.EAN),
            (
                constants.ConcertClub,
                models.ChronicleClubType.CONCERT_CLUB,
                models.ChronicleProductIdentifierType.OFFER_ID,
            ),
        ],
    )
    def test_save_chronicle_empty(self, club_constants, club_type, product_identifier_type):
        identifier = "1234567890123"
        identifier_choice_id = random_string()
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=club_constants.PRODUCT_IDENTIFIER_FIELD_ID.value,
                    choice_id=identifier_choice_id,
                    text=f" title - {identifier}",
                ),
                typeform.TypeformAnswer(
                    field_id=club_constants.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_chronicle(
            form=form,
            club_constants=club_constants,
            club_type=club_type,
            product_identifier_type=product_identifier_type,
        )

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.age is None
        assert chronicle.city is None
        assert chronicle.firstName is None
        assert chronicle.productIdentifier == identifier
        assert chronicle.productIdentifierType == product_identifier_type
        assert chronicle.identifierChoiceId == identifier_choice_id
        assert chronicle.content == "some random chronicle description"
        assert not chronicle.isIdentityDiffusible
        assert not chronicle.isSocialMediaDiffusible
        assert not chronicle.isActive
        assert chronicle.externalId == form.response_id
        assert chronicle.userId is None
        assert chronicle.clubType == club_type

    def test_save_chronicle_with_previous_products(self):
        identifier = "1234567890123"
        ean_choice_id = random_string()
        related_product = offers_factories.ProductFactory(ean=identifier)
        unrelated_product = offers_factories.ProductFactory()

        old_chronicle = chronicles_factories.ChronicleFactory(
            productIdentifier=identifier,
            productIdentifierType=models.ChronicleProductIdentifierType.EAN,
            identifierChoiceId=ean_choice_id,
            products=[related_product, unrelated_product],
        )

        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
                    choice_id=ean_choice_id,
                    text=identifier,
                ),
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.CHRONICLE_ID.value,
                    choice_id=None,
                    text="some random chronicle description",
                ),
            ],
        )

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        chronicle = db.session.query(models.Chronicle).filter(models.Chronicle.id != old_chronicle.id).first()
        assert len(chronicle.products) == 2
        assert related_product in chronicle.products
        assert unrelated_product in chronicle.products

    def test_do_not_save_chronicle_without_email(self):
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email=None,
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_chronicle_without_content(self):
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
                    choice_id=random_string(),
                    text="1234567890123",
                ),
            ],
        )

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_chronicle_without_product_identifier(self):
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        assert db.session.query(models.Chronicle).count() == 0

    def test_save_chronicle_link_to_user(self):
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
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        chronicle = db.session.query(models.Chronicle).first()
        assert chronicle.userId == user.id

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
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        chronicle = db.session.query(models.Chronicle).first()

        assert chronicle.products == [product]

    def test_save_chronicle_already_saved(self):
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
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        chronicles = db.session.query(models.Chronicle).all()
        assert len(chronicles) == 1
        assert chronicles[0].id == old_chronicle.id

    def test_save_chronicle_with_offers(self):
        ean = "1234567890123"
        ean_choice_id = random_string()
        offer = offers_factories.OfferFactory()
        old_chronicle = chronicles_factories.ChronicleFactory(
            offers=[offer], productIdentifier=ean, productIdentifierType=models.ChronicleProductIdentifierType.EAN
        )
        form = typeform.TypeformResponse(
            response_id=random_string(),
            date_submitted=datetime.datetime(2024, 10, 24),
            phone_number=None,
            email="email@mail.test",
            answers=[
                typeform.TypeformAnswer(
                    field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
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

        api.save_chronicle(
            form=form,
            club_constants=constants.BookClub,
            club_type=models.ChronicleClubType.BOOK_CLUB,
            product_identifier_type=models.ChronicleProductIdentifierType.EAN,
        )

        chronicle = db.session.query(models.Chronicle).filter(models.Chronicle.id != old_chronicle.id).one()
        assert chronicle.offers == [offer]


@pytest.mark.usefixtures("db_session")
class ExtractEanTest:
    @pytest.mark.parametrize(
        "text,result",
        [
            ("book title - 1234567890123 - december", "1234567890123"),
            ("1234567890123 - december", "1234567890123"),
            ("book title - 1234567890123", "1234567890123"),
            ("book title 2024 - 1234567890123 - december", "1234567890123"),
            ("book title 2024", None),
            ("book title", None),
            ("", None),
        ],
    )
    def test_extract_ean(self, text, result):
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text=text,
        )

        assert api._extract_ean(form) == result

    def test_choice_in_db(self):
        ean = "1234567890123"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text="nothing to see here",
        )
        chronicles_factories.ChronicleFactory(productIdentifier=ean, identifierChoiceId=choice_id)

        result = api._extract_ean(form)

        assert result == ean


@pytest.mark.usefixtures("db_session")
class ImportCineClubChroniclesTest:
    def _get_api_result(self):
        return [
            typeform.TypeformResponse(
                response_id=random_string(),
                date_submitted=datetime.datetime(2024, 10, 24),
                phone_number=None,
                email="email@mail.test",
                answers=[
                    typeform.TypeformAnswer(
                        field_id=random_string(),
                        choice_id=None,
                        text="should be ignored",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.CineClub.NAME_ID.value,
                        choice_id=None,
                        text="Bob",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.CineClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
                        choice_id=random_string(),
                        text="Movie Title - 285223 (sort le 11 juin)",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.CineClub.CHRONICLE_ID.value,
                        choice_id=None,
                        text=random_string(150),
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.CineClub.DIFFUSIBLE_PERSONAL_DATA_QUESTION_ID.value,
                        choice_id=constants.CineClub.DIFFUSIBLE_PERSONAL_DATA_ANSWER_ID.value,
                        text="oui",
                    ),
                    typeform.TypeformAnswer(
                        field_id=constants.CineClub.SOCIAL_MEDIA_QUESTION_ID.value,
                        choice_id=constants.CineClub.SOCIAL_MEDIA_ANSWER_ID.value,
                        text="oui",
                    ),
                ],
            ),
        ]

    def test_import_cine_club_chronicles_with_old_chronicle(self):
        old_chronicle = chronicles_factories.ChronicleFactory(
            clubType=models.ChronicleClubType.CINE_CLUB,
            productIdentifierType=models.ChronicleProductIdentifierType.ALLOCINE_ID,
        )
        api_results = self._get_api_result()

        with patch("pcapi.core.chronicles.api.typeform.get_responses", return_value=api_results) as typeform_mock:
            api.import_cine_club_chronicles()

            typeform_mock.assert_called_once_with(
                form_id=constants.CineClub.FORM_ID.value,
                num_results=pcapi_settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=old_chronicle.dateCreated,
                sort="submitted_at,asc",
            )

        chronicle = db.session.query(models.Chronicle).order_by(models.Chronicle.id.desc()).first()
        assert chronicle.email == "email@mail.test"

    def test_import_cine_club_chronicles_without_old_chronicle(self):
        api_results = self._get_api_result()

        with patch("pcapi.core.chronicles.api.typeform.get_responses", return_value=api_results) as typeform_mock:
            api.import_cine_club_chronicles()

            typeform_mock.assert_called_once_with(
                form_id=constants.CineClub.FORM_ID.value,
                num_results=pcapi_settings.TYPEFORM_IMPORT_CHUNK_SIZE,
                since=None,
                sort="submitted_at,asc",
            )

        chronicle = db.session.query(models.Chronicle).order_by(models.Chronicle.id.desc()).first()
        assert chronicle.email == "email@mail.test"


@pytest.mark.usefixtures("db_session")
class ExtractAllocineIdTest:
    @pytest.mark.parametrize(
        "text,result",
        [
            ("book title - 1000013371 - (sort le 18 juin)", "1000013371"),
            ("book title - 1000013371", "1000013371"),
            ("book title987654321 - 1000013371 - december", "1000013371"),
            ("book title 5000013371 - 1000013371 - december", "1000013371"),
            ("book title 5000013371", None),
            ("book title", None),
            ("", None),
        ],
    )
    def test_extract_allocine_id(self, text, result):
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.CineClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text=text,
        )

        assert api._extract_allocine_id(form) == result

    def test_choice_in_db(self):
        allocine_id = "1000013371"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.CineClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text="nothing to see here",
        )
        chronicles_factories.ChronicleFactory(productIdentifier=allocine_id, identifierChoiceId=choice_id)

        result = api._extract_allocine_id(form)

        assert result == allocine_id


@pytest.mark.usefixtures("db_session")
class ExtractOfferIdTest:
    @pytest.mark.parametrize(
        "text,result",
        [
            ("book title - 1234567890123 - december", "1234567890123"),
            ("1234567890123 - december", "1234567890123"),
            ("book title - 1234567890123", "1234567890123"),
            ("book title987654321 - 1234567890123 - december", "1234567890123"),
            ("book title 2024 - 1234567890123 - december", "1234567890123"),
            ("book title 2024", None),
            ("book title", None),
            ("", None),
        ],
    )
    def test_extract_offer_id(self, text, result):
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text=text,
        )

        assert api._extract_offer_id(form) == result

    def test_choice_in_db(self):
        offer_id = "1234567890123"
        choice_id = random_string()
        form = typeform.TypeformAnswer(
            field_id=constants.BookClub.PRODUCT_IDENTIFIER_FIELD_ID.value,
            choice_id=choice_id,
            text="nothing to see here",
        )
        chronicles_factories.ChronicleFactory(productIdentifier=offer_id, identifierChoiceId=choice_id)

        result = api._extract_offer_id(form)

        assert result == offer_id
