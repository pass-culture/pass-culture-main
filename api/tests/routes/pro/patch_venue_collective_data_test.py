import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_should_update_venue_with_no_empty_data(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            collectiveDomains=[],
            collectiveStudents=[],
            collectiveNetwork=[],
            collectiveDescription="",
            collectiveWebsite="",
            collectiveInterventionArea=[],
            venueEducationalStatusId=None,
            collectivePhone="",
            collectiveEmail="",
        )
        educational_status = offerers_factories.VenueEducationalStatusFactory()

        domain = educational_factories.EducationalDomainFactory(name="pouet")

        client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = {
            "collectiveDomains": [domain.id],
            "collectiveStudents": [educational_models.StudentLevels.COLLEGE4.value],
            "collectiveNetwork": ["network1", "network2"],
            "collectiveDescription": "Description",
            "collectiveWebsite": "http://website.com",
            "collectiveInterventionArea": ["01", "02"],
            "venueEducationalStatusId": educational_status.id,
            "collectivePhone": "0600000000",
            "collectiveEmail": "john@doe.com",
        }

        response = client.patch(f"/venues/{humanize(venue.id)}/collective-data", json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.get(venue_id)
        assert venue.collectiveDomains == [domain]
        assert venue.collectiveStudents == [educational_models.StudentLevels.COLLEGE4]
        assert venue.collectiveNetwork == ["network1", "network2"]
        assert venue.collectiveDescription == "Description"
        assert venue.collectiveWebsite == "http://website.com"
        assert venue.collectiveInterventionArea == ["01", "02"]
        assert venue.venueEducationalStatusId == educational_status.id
        assert venue.collectivePhone == "0600000000"
        assert venue.collectiveEmail == "john@doe.com"

    def test_should_update_venue_with_empty_data(self, client) -> None:
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        domain = educational_factories.EducationalDomainFactory(name="pouet")
        educational_status_1 = offerers_factories.VenueEducationalStatusFactory()

        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            collectiveDomains=[domain],
            collectiveStudents=[educational_models.StudentLevels.COLLEGE4],
            collectiveNetwork=["network1", "network2"],
            collectiveDescription="Description",
            collectiveWebsite="http://website.com",
            collectiveInterventionArea=["01", "02"],
            venueEducationalStatusId=educational_status_1.id,
            collectivePhone="0600000000",
            collectiveEmail="john@doe.com",
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = {
            "collectiveDomains": [],
            "collectiveStudents": [],
            "collectiveNetwork": [],
            "collectiveDescription": None,
            "collectiveWebsite": None,
            "collectiveInterventionArea": [],
            "venueEducationalStatusId": None,
            "collectivePhone": None,
            "collectiveEmail": None,
        }

        response = client.patch(f"/venues/{humanize(venue.id)}/collective-data", json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.get(venue_id)
        assert venue.collectiveDomains == []
        assert venue.collectiveStudents == []
        assert venue.collectiveNetwork == []
        assert venue.collectiveDescription == None
        assert venue.collectiveWebsite == None
        assert venue.collectiveInterventionArea == []
        assert venue.venueEducationalStatusId == None
        assert venue.collectivePhone == None
        assert venue.collectiveEmail == None

    def test_should_update_venue_when_specifying_some_data(self, client) -> None:
        # given
        domain = educational_factories.EducationalDomainFactory(name="pouet")
        user_offerer = offerers_factories.UserOffererFactory()
        educational_status_1 = offerers_factories.VenueEducationalStatusFactory()
        educational_status_2 = offerers_factories.VenueEducationalStatusFactory()

        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            collectiveDomains=[domain],
            collectiveStudents=[educational_models.StudentLevels.COLLEGE4],
            collectiveNetwork=["network1", "network2"],
            collectiveDescription="Description",
            collectiveWebsite="http://website.com",
            collectiveInterventionArea=["01", "02"],
            venueEducationalStatusId=educational_status_1.id,
            collectivePhone="0600000000",
            collectiveEmail="john@doe.com",
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        venue_data = {
            "collectiveNetwork": ["network3"],
            "collectiveDescription": "Une autre description",
            "venueEducationalStatusId": educational_status_2.id,
        }

        response = client.patch(f"/venues/{humanize(venue.id)}/collective-data", json=venue_data)

        # then
        assert response.status_code == 200
        venue = offerers_models.Venue.query.get(venue_id)
        assert venue.collectiveDomains == [domain]
        assert venue.collectiveStudents == [educational_models.StudentLevels.COLLEGE4]
        assert venue.collectiveNetwork == ["network3"]
        assert venue.collectiveDescription == "Une autre description"
        assert venue.collectiveInterventionArea == ["01", "02"]
        assert venue.venueEducationalStatusId == educational_status_2.id
        assert venue.collectivePhone == "0600000000"
        assert venue.collectiveEmail == "john@doe.com"
