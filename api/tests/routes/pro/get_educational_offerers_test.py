import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


class GetEducationalOfferersTest:
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
        )
        venue_offerer_2 = offerers_factories.CollectiveVenueFactory(managingOfferer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=not_validated_offerer)

        # when
        queries = testing.AUTHENTICATION_QUERIES
        queries += 1  # select offerers
        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(queries):
            response = client.get("/offerers/educational")
            assert response.status_code == 200

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
                        }
                    ],
                },
            ]
        }
