""" local providers test """
import json

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from local_providers import OpenAgendaEvents
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider
from tests.conftest import clean_database

from tests.test_utils import provider_test, check_open_agenda_api_is_down, create_offerer, create_venue


def get_data_from_sandbox_files(page):
    with open(Path(os.path.dirname(os.path.realpath(__file__)))
              / '..' / '..' / 'sandboxes' / 'providers'
              / ('openagenda' + str(page) + '.json')) as f:
        return json.load(f)


@pytest.mark.standalone
class OpenAgendaEventsTest:

    @pytest.mark.skipif(check_open_agenda_api_is_down(), reason="Open Agenda API is down")
    @clean_database
    @patch('local_providers.openagenda_events.get_data')
    def test_open_agenda_events_creaet_data_from_sandboxe_file(self, get_data, app):
        # mock
        open_agenda_sandboxes_files = [1, 2]
        sandboxes_data = []
        for page in open_agenda_sandboxes_files:
            data_content = get_data_from_sandbox_files(page)
            sandboxes_data.append(data_content)

        get_data.side_effect = sandboxes_data

        # given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, name='Librairie OpenAgenda', siret='12345678901231')
        PcObject.check_and_save(venue)
        venue_id = venue.id

        open_agenda_provider = Provider.getByClassName('OpenAgendaEvents')
        venue_provider = VenueProvider()
        venue_provider.venueId = venue_id
        venue_provider.provider = open_agenda_provider
        venue_provider.isActive = True
        venue_provider.venueIdAtOfferProvider = '49050769'
        PcObject.check_and_save(venue_provider)
        venue_provider = VenueProvider.query \
            .filter_by(venueIdAtOfferProvider='49050769') \
            .one_or_none()
        provider_test(app,
                      OpenAgendaEvents,
                      venue_provider,
                      checkedObjects=18,
                      createdObjects=18,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=3,
                      createdThumbs=3,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Event=3,
                      EventOccurrence=12,
                      Offer=3,
                      Stock=0,
                      Venue=0,
                      Offerer=0)
