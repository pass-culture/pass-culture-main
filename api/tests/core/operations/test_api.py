import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors import typeform
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import models as operations_models


pytestmark = pytest.mark.usefixtures("db_session")


class CreateSpecialEventFromTypeformTest:
    @patch(
        "pcapi.connectors.typeform.get_form",
        return_value=typeform.TypeformForm(
            form_id="test",
            title="Mon questionnaire",
            date_created=datetime.datetime.now() - datetime.timedelta(days=3),
            fields=[
                typeform.TypeformQuestion(field_id="question1", title="Quel est ton prénom ?"),
                typeform.TypeformQuestion(field_id="question2", title="Que penses-tu de ce test ?"),
            ],
        ),
    )
    def test_create_special_event_from_typeform(self, mock_get_form):
        venue = offerers_factories.VenueFactory()
        event_date = datetime.datetime.now() + datetime.timedelta(days=15)

        special_event_id = operations_api.create_special_event_from_typeform(
            "test", event_date=event_date, venue_id=venue.id
        ).id

        special_event = operations_models.SpecialEvent.query.one()
        assert special_event.id == special_event_id
        assert special_event.externalId == "test"
        assert special_event.title == "Mon questionnaire"
        assert special_event.eventDate == event_date
        assert special_event.offererId == venue.managingOffererId
        assert special_event.venueId == venue.id

        questions = operations_models.SpecialEventQuestion.query.order_by(
            operations_models.SpecialEventQuestion.externalId
        ).all()
        assert len(questions) == 2
        assert questions[0].externalId == "question1"
        assert questions[0].title == "Quel est ton prénom ?"
        assert questions[1].externalId == "question2"
        assert questions[1].title == "Que penses-tu de ce test ?"

    def test_check_offerer_and_venue_consistency(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory()

        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform("test", offerer_id=offerer.id, venue_id=venue.id)
        assert "n'appartient pas à la structure" in str(err.value)

    def test_check_offerer_exists(self):
        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform("test", offerer_id=999999)
        assert "n'existe pas" in str(err.value)

    def test_check_venue_exists(self):
        with pytest.raises(ValueError) as err:
            operations_api.create_special_event_from_typeform("test", venue_id=999999)
        assert "n'existe pas" in str(err.value)
