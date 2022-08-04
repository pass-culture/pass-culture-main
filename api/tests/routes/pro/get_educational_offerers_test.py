import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


class GetEducationalOfferersTest:
    @pytest.mark.usefixtures("db_session")
    def test_response_serializer_for_multiple_educational_offerers(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        not_validated_offerer = offerers_factories.OffererFactory(validationToken="validationToken")
        venue_offerer_1 = offerers_factories.VenueFactory(managingOfferer=offerer_1, collectiveInterventionArea=None)
        venue_offerer_2 = offerers_factories.VenueFactory(managingOfferer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=not_validated_offerer)

        # when
        response = client.with_session_auth(pro_user.email).get("/offerers/educational")

        # then
        assert response.status_code == 200
        assert response.json == {
            "educationalOfferers": [
                {
                    "id": humanize(offerer_1.id),
                    "name": offerer_1.name,
                    "managedVenues": [
                        {
                            "address": venue_offerer_1.address,
                            "audioDisabilityCompliant": venue_offerer_1.audioDisabilityCompliant,
                            "city": venue_offerer_1.city,
                            "id": humanize(venue_offerer_1.id),
                            "isVirtual": venue_offerer_1.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_1.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_1.motorDisabilityCompliant,
                            "publicName": venue_offerer_1.publicName,
                            "postalCode": venue_offerer_1.postalCode,
                            "visualDisabilityCompliant": venue_offerer_1.visualDisabilityCompliant,
                            "name": venue_offerer_1.name,
                            "collectiveInterventionArea": None,
                        }
                    ],
                },
                {
                    "id": humanize(offerer_2.id),
                    "name": offerer_2.name,
                    "managedVenues": [
                        {
                            "address": venue_offerer_2.address,
                            "audioDisabilityCompliant": venue_offerer_2.audioDisabilityCompliant,
                            "city": venue_offerer_2.city,
                            "id": humanize(venue_offerer_2.id),
                            "isVirtual": venue_offerer_2.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_2.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_2.motorDisabilityCompliant,
                            "publicName": venue_offerer_2.publicName,
                            "postalCode": venue_offerer_2.postalCode,
                            "visualDisabilityCompliant": venue_offerer_2.visualDisabilityCompliant,
                            "name": venue_offerer_2.name,
                            "collectiveInterventionArea": ["75", "92"],
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
        offerers_factories.OffererFactory(validationToken="validationToken")
        offerers_factories.VenueFactory(managingOfferer=offerer_1)
        offerers_factories.VenueFactory(managingOfferer=offerer_2)

        # when
        response = client.with_session_auth(admin_user.email).get("/offerers/educational")

        # then
        assert response.status_code == 400

    @pytest.mark.usefixtures("db_session")
    def test_response_serializer_for_admin(self, client):
        # given
        admin_user = users_factories.AdminFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer_1)
        venue_offerer_2 = offerers_factories.VenueFactory(managingOfferer=offerer_2)

        # when
        api_url = f"/offerers/educational?offerer_id={humanize(offerer_2.id)}"
        response = client.with_session_auth(admin_user.email).get(api_url)

        # then
        assert response.status_code == 200
        assert response.json == {
            "educationalOfferers": [
                {
                    "id": humanize(offerer_2.id),
                    "name": offerer_2.name,
                    "managedVenues": [
                        {
                            "address": venue_offerer_2.address,
                            "audioDisabilityCompliant": venue_offerer_2.audioDisabilityCompliant,
                            "city": venue_offerer_2.city,
                            "id": humanize(venue_offerer_2.id),
                            "isVirtual": venue_offerer_2.isVirtual,
                            "mentalDisabilityCompliant": venue_offerer_2.mentalDisabilityCompliant,
                            "motorDisabilityCompliant": venue_offerer_2.motorDisabilityCompliant,
                            "publicName": venue_offerer_2.publicName,
                            "postalCode": venue_offerer_2.postalCode,
                            "visualDisabilityCompliant": venue_offerer_2.visualDisabilityCompliant,
                            "name": venue_offerer_2.name,
                            "collectiveInterventionArea": ["75", "92"],
                        }
                    ],
                },
            ]
        }
