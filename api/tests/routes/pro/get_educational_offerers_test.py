import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


class GetEducationalOfferersTest:
    # 1. user
    # 2. session
    # 3. DELETE from user_session
    # 4. user
    # 5. INSERT into user_session
    # 6. user
    # 7. UPDATE user
    # 8. user
    # 9. user !TODO check why there is so many select of user and queries in general
    # 10. user
    # 11. SELECT EXISTS collective offer
    # 12. offerer
    # 13. feature
    # 14.  user_pro_new_nav_state
    # 15. SELECT EXISTS user_offerer
    # 16. user_session
    # 17. user
    # 18. offerer
    expected_num_queries = 18

    @pytest.mark.usefixtures("db_session")
    def test_response_serializer_for_multiple_educational_offerers(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        not_validated_offerer = offerers_factories.NotValidatedOffererFactory()
        venue_offerer_1 = offerers_factories.VenueFactory(
            managingOfferer=offerer_1,
            collectiveInterventionArea=None,
            collectivePhone="0601020304",
            collectiveEmail="test@example.com",
            collectiveSubCategoryId="SPECTACLE_REPRESENTATION",
        )
        venue_offerer_2 = offerers_factories.CollectiveVenueFactory(managingOfferer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=not_validated_offerer)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = client.with_session_auth(pro_user.email).get("/offerers/educational")
            assert response.status_code == 200

        # then

        assert response.json == {
            "educationalOfferers": [
                {
                    "id": offerer_1.id,
                    "name": offerer_1.name,
                    "allowedOnAdage": offerer_1.allowedOnAdage,
                    "managedVenues": [
                        {
                            "audioDisabilityCompliant": venue_offerer_1.audioDisabilityCompliant,
                            "city": venue_offerer_1.city,
                            "id": venue_offerer_1.id,
                            "isVirtual": venue_offerer_1.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_1.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_1.motorDisabilityCompliant,
                            "publicName": venue_offerer_1.publicName,
                            "postalCode": venue_offerer_1.postalCode,
                            "street": venue_offerer_1.street,
                            "visualDisabilityCompliant": venue_offerer_1.visualDisabilityCompliant,
                            "name": venue_offerer_1.name,
                            "collectiveInterventionArea": None,
                            "collectivePhone": "0601020304",
                            "collectiveEmail": "test@example.com",
                            "collectiveSubCategoryId": venue_offerer_1.collectiveSubCategoryId,
                        }
                    ],
                },
                {
                    "id": offerer_2.id,
                    "name": offerer_2.name,
                    "allowedOnAdage": offerer_2.allowedOnAdage,
                    "managedVenues": [
                        {
                            "audioDisabilityCompliant": venue_offerer_2.audioDisabilityCompliant,
                            "city": venue_offerer_2.city,
                            "id": venue_offerer_2.id,
                            "isVirtual": venue_offerer_2.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_2.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_2.motorDisabilityCompliant,
                            "publicName": venue_offerer_2.publicName,
                            "postalCode": venue_offerer_2.postalCode,
                            "street": venue_offerer_2.street,
                            "visualDisabilityCompliant": venue_offerer_2.visualDisabilityCompliant,
                            "name": venue_offerer_2.name,
                            "collectiveInterventionArea": ["75", "92"],
                            "collectivePhone": None,
                            "collectiveEmail": None,
                            "collectiveSubCategoryId": venue_offerer_2.collectiveSubCategoryId,
                        }
                    ],
                },
            ]
        }

    @pytest.mark.usefixtures("db_session")
    def test_error_when_missing_offerer_id_query_param_for_admin_user(self, client):
        # given
        admin_user = users_factories.AdminFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerers_factories.NotValidatedOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer_1)
        offerers_factories.VenueFactory(managingOfferer=offerer_2)

        # when
        with assert_num_queries(
            self.expected_num_queries + 1
        ):  # !TODO still too many queries, need to check number queries
            response = client.with_session_auth(admin_user.email).get("/offerers/educational")
            assert response.status_code == 400

        # then

    @pytest.mark.usefixtures("db_session")
    def test_response_serializer_for_admin(self, client):
        # given
        admin_user = users_factories.AdminFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerers_factories.CollectiveVenueFactory(managingOfferer=offerer_1)
        venue_offerer_2 = offerers_factories.CollectiveVenueFactory(managingOfferer=offerer_2)

        # when
        api_url = f"/offerers/educational?offerer_id={offerer_2.id}"
        with assert_num_queries(20):  # !TODO still too many queries, need investigation
            response = client.with_session_auth(admin_user.email).get(api_url)
            assert response.status_code == 200

        # then
        assert response.json == {
            "educationalOfferers": [
                {
                    "id": offerer_2.id,
                    "name": offerer_2.name,
                    "allowedOnAdage": offerer_2.allowedOnAdage,
                    "managedVenues": [
                        {
                            "audioDisabilityCompliant": venue_offerer_2.audioDisabilityCompliant,
                            "city": venue_offerer_2.city,
                            "id": venue_offerer_2.id,
                            "isVirtual": venue_offerer_2.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_2.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_2.motorDisabilityCompliant,
                            "publicName": venue_offerer_2.publicName,
                            "postalCode": venue_offerer_2.postalCode,
                            "street": venue_offerer_2.street,
                            "visualDisabilityCompliant": venue_offerer_2.visualDisabilityCompliant,
                            "name": venue_offerer_2.name,
                            "collectiveInterventionArea": ["75", "92"],
                            "collectivePhone": None,
                            "collectiveEmail": None,
                            "collectiveSubCategoryId": venue_offerer_2.collectiveSubCategoryId,
                        }
                    ],
                },
            ]
        }
