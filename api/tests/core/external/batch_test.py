from copy import deepcopy

import pytest
import requests_mock

from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.batch import testing as batch_testing
from pcapi.core.external.batch.api import update_user_attributes
from pcapi.core.external.batch.attributes import format_user_attributes
from pcapi.core.external.batch.backends.batch import BatchAPI
from pcapi.core.external.batch.backends.batch import BatchBackend
from pcapi.core.external.batch.transactional_notifications import TransactionalNotificationDataV2
from pcapi.core.external.batch.transactional_notifications import TransactionalNotificationMessageV2
from pcapi.core.external.batch.utils import batch_length
from pcapi.core.external.batch.utils import shorten_for_batch

from . import common_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")

MAX_BATCH_PARAMETER_SIZE = 30


def test_update_user_attributes():
    user_id = 123
    attributes = {"param": "value"}

    update_user_attributes(BatchAPI.IOS, user_id, attributes)

    assert batch_testing.requests == [
        {
            "attribute_values": {"param": "value"},
            "batch_api": "IOS",
            "user_id": 123,
            "can_be_asynchronously_retried": False,
        }
    ]


class FormatUserAttributesTest:
    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(common_user_attributes)

        assert formatted_attributes == {
            "date(u.date_of_birth)": "2003-05-06T00:00:00",
            "date(u.date_created)": "2021-02-06T00:00:00",
            "date(u.deposit_activation_date)": None,
            "date(u.deposit_expiration_date)": None,
            "date(u.last_booking_date)": "2021-05-06T00:00:00",
            "date(u.product_brut_x_use)": "2021-05-06T00:00:00",
            "u.credit": 48000,
            "u.bonification_status": "eligible",
            "u.booked_offer_categories_count": 2,
            "u.booking_count": 4,
            "u.booking_venues_count": 3,
            "u.city": "Rodez",
            "u.departement_code": "12",
            "u.deposits_count": 1,
            "u.first_name": "First name",
            "u.has_completed_id_check": True,
            "u.is_beneficiary": True,
            "u.is_current_beneficiary": True,
            "u.is_former_beneficiary": False,
            "u.last_name": "Last name",
            "u.last_recredit_type": None,
            "u.most_booked_movie_genre": "COMEDY",
            "u.most_booked_music_type": "900",
            "u.most_booked_subcategory": "CINE_PLEIN_AIR",
            "ut.booking_categories": ["CINEMA", "LIVRE"],
            "ut.booking_subcategories": ["ABO_LIVRE_NUMERIQUE", "CARTE_CINE_ILLIMITE", "CINE_PLEIN_AIR"],
            "ut.most_favorite_offer_subcat": ["CINE_PLEIN_AIR", "SUPPORT_PHYSIQUE_FILM"],
            "u.marketing_email_subscription": True,
            "u.marketing_push_subscription": True,
            "ut.permanent_theme_preference": ["cinema"],
            "u.postal_code": None,
            "ut.roles": ["BENEFICIARY"],
            "u.eligibility": "age-18",
            "u.is_eligible": True,
        }

        # ensure attributes keys are shorter than MAX_BATCH_PARAMETER_SIZE
        for attribute in formatted_attributes:
            if attribute.startswith("date"):
                attribute = attribute[5:-1]

            parameter_name = attribute.split(".")[1]
            assert len(parameter_name) <= MAX_BATCH_PARAMETER_SIZE

        assert "ut.intended_categories" not in formatted_attributes

    def test_format_attributes_without_bookings(self):
        attributes = deepcopy(common_user_attributes)
        attributes.booking_categories = []
        attributes.last_booking_date = None

        formatted_attributes = format_user_attributes(attributes)

        assert formatted_attributes["date(u.last_booking_date)"] is None
        assert "ut.booking_categories" not in formatted_attributes

    def test_format_attributes_with_cultural_survey_answers(self):
        cultural_survey_answers = {
            cultural_survey_models.CulturalSurveyQuestionEnum.SORTIES.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL.value,
            ],
            cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.PROJECTION_CONCERT.value,
                cultural_survey_models.CulturalSurveyAnswerEnum.PROJECTION_FESTIVAL.value,
            ],
        }

        formatted_attributes = format_user_attributes(
            common_user_attributes, cultural_survey_answers=cultural_survey_answers
        )

        assert formatted_attributes["ut.intended_categories"] == ["PROJECTION_CONCERT", "PROJECTION_FESTIVAL"]

    def test_format_attributes_with_empty_cultural_survey_answers(self):
        cultural_survey_answers = {
            cultural_survey_models.CulturalSurveyQuestionEnum.SORTIES.value: [],
            cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value: [],
        }

        formatted_attributes = format_user_attributes(
            common_user_attributes, cultural_survey_answers=cultural_survey_answers
        )

        # A Batch tag can't be an empty list, otherwise the API returns an error
        assert "ut.intended_categories" not in formatted_attributes

    def test_format_user_attributes_with_achievements(self):
        attributes = deepcopy(common_user_attributes)
        attributes.achievements = ["FIRST_MOVIE_BOOKING"]

        formatted = format_user_attributes(attributes)

        assert "ut.achievements" in formatted
        assert isinstance(formatted["ut.achievements"], list)
        assert formatted["ut.achievements"] == ["FIRST_MOVIE_BOOKING"]


class BatchPushNotificationClientTest:
    def test_update_user_attributes(self):
        with requests_mock.Mocker() as mock:
            ios_post = mock.post("https://api.batch.com/1.0/fake_android_api_key/data/users/1")

            BatchBackend().update_user_attributes(BatchAPI.ANDROID, 1, {"attri": "but"})

            assert ios_post.last_request.json() == {"overwrite": False, "values": {"attri": "but"}}

    def test_send_transactional_notification(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.batch.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.batch.com/1.1/fake_ios_api_key/transactional/send")

            BatchBackend().send_transactional_notification(
                TransactionalNotificationDataV2(
                    group_id="Group_id",
                    user_ids=[1234, 4321],
                    message=TransactionalNotificationMessageV2(title="Putsch", body="Notif"),
                )
            )

            assert ios_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }
            assert android_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }

    def test_api_exception(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.batch.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.batch.com/1.1/fake_ios_api_key/transactional/send")

            BatchBackend().send_transactional_notification(
                TransactionalNotificationDataV2(
                    group_id="Group_id",
                    user_ids=[1234, 4321],
                    message=TransactionalNotificationMessageV2(title="Putsch", body="Notif"),
                )
            )

            assert ios_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }
            assert android_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }


class ShortenForBatchTest:
    def test_batch_length_no_emoji(self):
        s = "Hello World"
        # Without emojis, batch_length should equal the standard length
        assert batch_length(s) == len(s)

    def test_batch_length_with_emoji(self):
        s = "Hello 😎"
        # "Hello " = 6 characters, "😎" counts as 2, so total should be 8
        assert batch_length(s) == 8

    def test_batch_length_multiple_emojis(self):
        s = "😎😎"
        # Each emoji counts as 2, total should be 4
        assert batch_length(s) == 4

    def test_batch_length_complex_emojis(self):
        # Test with various complex emoji types:
        # - Combined emojis (family, couples)
        # - Skin tone modifiers
        # - Flags
        # - ZWJ sequences (professional emojis)
        # - Directional text emojis
        s = "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈👨🏾‍🦰🫂🇫🇷🤌🦾🧬🎭"
        # Each complex emoji sequence counts differently:
        # 👨‍👩‍👧‍👦 (family) = 8 (4 people joined)
        # 👩🏽‍💻 (woman technologist with medium skin tone) = 4
        # 🏳️‍🌈 (rainbow flag) = 4 (+ 1 for the variation selector)
        # 👨🏾‍🦰 (man with afro and medium-dark skin tone) = 4
        # 🫂 (people hugging) = 2
        # 🇫🇷 (flag) = 4
        # 🤌 (pinched fingers) = 2
        # 🦾 (mechanical arm) = 2
        # 🧬 (dna) = 2
        # 🎭 (performing arts) = 2
        # Total expected length = 35
        assert batch_length(s) == 35

    def test_shorten_for_batch_no_truncation(self):
        s = "Hello World"
        max_length = 20
        # The string is shorter than max_length, so it should be returned unchanged
        assert shorten_for_batch(s, max_length) == s

    def test_shorten_for_batch_truncation_no_emoji(self):
        s = "Hello World, this is a long text"
        max_length = 10
        result = shorten_for_batch(s, max_length)
        # The result should end with the placeholder and not exceed max_length when measured with batch_length
        assert result.endswith("...")
        assert batch_length(result) == max_length

    def test_shorten_for_batch_truncation_no_emoji_preserve_words(self):
        s = "Hello World, this is a long text"
        max_length = 10
        result = shorten_for_batch(s, max_length, preserve_words=True)
        assert result == "Hello..."

    def test_shorten_for_batch_truncation_with_emoji(self):
        s = "Hello 😎, this is a long text with emojis 😎😎"
        max_length = 20
        result = shorten_for_batch(s, max_length)
        # The result should end with the placeholder and its batch length should not exceed max_length
        assert result.endswith("...")
        assert batch_length(result) == max_length

    def test_shorten_for_batch_truncation_with_emoji_preserve_words(self):
        s = "Hello 😎, this is a long text with emojis 😎😎"
        max_length = 25
        result = shorten_for_batch(s, max_length, preserve_words=True)
        assert result == "Hello 😎, this is a..."

    def test_shorten_for_batch_exact_boundary(self):
        # Construct a string where the batch length equals max_length exactly, so no truncation occurs.
        s = "Hello😎"  # "Hello" = 5, "😎" = 2, total = 7
        max_length = 7
        result = shorten_for_batch(s, max_length)
        # Since the string already fits the max_length, it should be returned unchanged.
        assert result == s

    def test_shorten_for_batch_complex_emojis(self):
        s = "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈👨🏾‍🦰🫂🇫🇷🤌🦾🧬🎭"
        # Each complex emoji sequence counts differently:
        # 👨‍👩‍👧‍👦 (family) = 8 (4 people joined)
        # 👩🏽‍💻 (woman technologist with medium skin tone) = 4
        # 🏳️‍🌈 (rainbow flag) = 4
        # 👨🏾‍🦰 (man with afro and medium-dark skin tone) = 4
        # 🫂 (people hugging) = 2
        # 🇫🇷 (flag) = 4
        # 🤌 (pinched fingers) = 2
        # 🦾 (mechanical arm) = 2
        # 🧬 (dna) = 2
        # 🎭 (performing arts) = 2
        max_length = 20
        result = shorten_for_batch(s, max_length, preserve_words=True)
        assert result == "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈..."

    def test_shorten_for_batch_variation_selector(self):
        assert batch_length("🗝️") == 3  # 2 for the keycap and 1 for the variation selector
        s = "🗝️Escape Game à Paris - Entretien avec Gustave Eiffel | Tarif sur le site de l'offre"
        max_length = 64
        result = shorten_for_batch(s, max_length)
        assert result.endswith("...")
        assert result == "🗝️Escape Game à Paris - Entretien avec Gustave Eiffel | Tari..."
        assert batch_length(result) <= max_length
