from copy import deepcopy

import pytest

from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.batch import format_user_attributes

from . import common_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")

MAX_BATCH_PARAMETER_SIZE = 30


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
            "u.most_booked_movie_genre": "COMEDY",
            "u.most_booked_music_type": "900",
            "u.most_booked_subcategory": "CINE_PLEIN_AIR",
            "ut.booking_categories": ["CINEMA", "LIVRE"],
            "ut.booking_subcategories": ["ABO_LIVRE_NUMERIQUE", "CARTE_CINE_ILLIMITE", "CINE_PLEIN_AIR"],
            "ut.most_favorite_offer_subcat": ["CINE_PLEIN_AIR", "SUPPORT_PHYSIQUE_FILM"],
            "u.marketing_push_subscription": True,
            "u.postal_code": None,
            "ut.roles": ["BENEFICIARY"],
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

        assert formatted_attributes["date(u.last_booking_date)"] == None
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
