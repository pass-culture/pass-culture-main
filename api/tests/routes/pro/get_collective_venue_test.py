import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_has_rights_on_managing_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            collectiveDescription="une description avec des accents éç",
            collectiveDomains=[educational_factories.EducationalDomainFactory()],
            collectiveEmail="pouet@example.com",
            collectiveInterventionArea=["un lieu", "un autre lieu", "un kiwi"],
            venueEducationalStatus=offerers_factories.VenueEducationalStatusFactory(),
            collectiveNetwork=["un réseau", "un partenaire", "une orange"],
            collectivePhone="0199001234",
            collectiveStudents=[educational_models.StudentLevels.COLLEGE3, educational_models.StudentLevels.GENERAL1],
            collectiveWebsite="https://passculture.app",
        )
        expected_serialized_venue = {
            "id": humanize(venue.id),
            "collectiveAccessInformation": None,
            "collectiveDescription": venue.collectiveDescription,
            "collectiveDomains": [
                {
                    "id": venue.collectiveDomains[0].id,
                    "name": venue.collectiveDomains[0].name,
                }
            ],
            "collectiveEmail": venue.collectiveEmail,
            "collectiveInterventionArea": venue.collectiveInterventionArea,
            "collectiveNetwork": venue.collectiveNetwork,
            "collectivePhone": venue.collectivePhone,
            "collectiveLegalStatus": {
                "id": venue.venueEducationalStatus.id,
                "name": venue.venueEducationalStatus.name,
            },
            "collectiveStudents": [
                educational_models.StudentLevels.COLLEGE3.value,
                educational_models.StudentLevels.GENERAL1.value,
            ],
            "collectiveWebsite": venue.collectiveWebsite,
        }

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s/collective-data" % humanize(venue.id))

        assert response.status_code == 200
        assert response.json == expected_serialized_venue
