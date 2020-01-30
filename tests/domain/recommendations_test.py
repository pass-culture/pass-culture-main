from domain.build_recommendations import move_requested_recommendation_first
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_recommendation, \
    create_mediation
from tests.model_creators.specific_creators import create_offer_with_thing_product


class MoveRequestedRecommendationFirstTest:
    @clean_database
    def test_move_requested_recommendation_first_when_second_reco_requested(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        mediation3 = create_mediation(offer3)
        recommendations = [
            create_recommendation(offer1, user=user, mediation=mediation1),
            create_recommendation(offer2, user=user, mediation=mediation2),
            create_recommendation(offer3, user=user, mediation=mediation3),
        ]
        repository.save(mediation1, mediation2, mediation3, *recommendations)
        requested_recommendation = recommendations[1]

        # When
        ordered_recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)

        # Then
        assert ordered_recommendations[0] == requested_recommendation
        assert len(ordered_recommendations) == len(recommendations)

    @clean_database
    def test_move_requested_recommendation_first_when_tuto_in_recommendations(self, app):
        # Given
        user = create_user()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        tuto_mediation = create_mediation(None, tuto_index=0)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        mediation3 = create_mediation(offer3)
        recommendations = [
            create_recommendation(None, user=user, mediation=tuto_mediation),
            create_recommendation(offer1, user=user, mediation=mediation1),
            create_recommendation(offer2, user=user, mediation=mediation2),
            create_recommendation(offer3, user=user, mediation=mediation3),
        ]
        repository.save(mediation1, mediation2, mediation3, *recommendations)

        # When
        requested_recommendation = recommendations[3]
        ordered_recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)

        # Then
        assert ordered_recommendations[0] == requested_recommendation
        assert len(ordered_recommendations) == len(recommendations)

    @clean_database
    def test_move_requested_recommendation_first_when_tuto_requested(self, app):
        # Given
        user = create_user()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        tuto_mediation = create_mediation(None, tuto_index=0)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        mediation3 = create_mediation(offer3)
        recommendations = [
            create_recommendation(offer1, user=user, mediation=mediation1),
            create_recommendation(None, user=user, mediation=tuto_mediation),
            create_recommendation(offer2, user=user, mediation=mediation2),
            create_recommendation(offer3, user=user, mediation=mediation3),
        ]
        repository.save(mediation1, mediation2, mediation3, *recommendations)

        # When
        requested_recommendation = recommendations[1]
        ordered_recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)

        # Then
        assert ordered_recommendations[0] == requested_recommendation
        assert len(ordered_recommendations) == len(recommendations)

    @clean_database
    def test_move_requested_tuto_index_1_first_when_tuto_2_in_recommendations(self, app):
        # Given
        user = create_user()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        tuto_mediation1 = create_mediation(None, tuto_index=1)
        tuto_mediation2 = create_mediation(None, tuto_index=2)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        mediation3 = create_mediation(offer3)
        recommendations = [
            create_recommendation(offer1, user=user, mediation=mediation1),
            create_recommendation(None, user=user, mediation=tuto_mediation2),
            create_recommendation(None, user=user, mediation=tuto_mediation1),
            create_recommendation(offer2, user=user, mediation=mediation2),
            create_recommendation(offer3, user=user, mediation=mediation3),
        ]

        requested_recommendation = create_recommendation(None, user=user, mediation=tuto_mediation1)

        repository.save(mediation1, mediation2, mediation3, *recommendations)

        # When
        ordered_recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)

        # Then
        assert ordered_recommendations[0] == requested_recommendation
        assert len(ordered_recommendations) == len(recommendations)

    @clean_database
    def test_move_requested_matching_offer_first_when_other_recommendation_is_requested_with_different_mediation(self,
                                                                                                                 app):
        # Given
        user = create_user()

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        mediation3 = create_mediation(offer3)
        recommendations = [
            create_recommendation(offer1, user=user, mediation=mediation1),
            create_recommendation(offer2, user=user, mediation=mediation2),
            create_recommendation(offer3, user=user, mediation=mediation3),
        ]

        requested_recommendation = create_recommendation(offer2, user=user, mediation=create_mediation(offer2))

        repository.save(mediation1, mediation2, mediation3, *recommendations)

        # When
        ordered_recommendations = move_requested_recommendation_first(recommendations, requested_recommendation)

        # Then
        assert ordered_recommendations[0] == requested_recommendation
        assert len(ordered_recommendations) == len(recommendations)
        assert recommendations[1] not in ordered_recommendations
