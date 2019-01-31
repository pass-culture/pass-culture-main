""" local providers test """
import pytest
from sqlalchemy import func

from local_providers import OpenAgendaEvents, \
                            SpreadsheetExpStocks, \
                            SpreadsheetExpVenues, \
                            TiteLiveThingDescriptions, \
                            TiteLiveThingThumbs, \
                            TiteLiveThings, \
                            TiteLiveVenues
from models.db import db
from models.pc_object import PcObject
from models.provider import Provider
from models.thing import Thing
from models.venue_provider import VenueProvider
from sandboxes.scripts.creators.handmade import save_handmade_sandbox
from utils.human_ids import dehumanize
from utils.logger import logger
from utils.test_utils import assertCreatedCounts, \
    assert_created_thumbs, \
    assertEmptyDb, \
    provider_test, \
    saveCounts,\
    check_open_agenda_api_is_down

savedCounts = {}


def test_10_titelive_venues_provider(app):
    assertEmptyDb(app)
    assert_created_thumbs()
    provider_test(app,
                  TiteLiveVenues,
                  None,
                  checkedObjects=6,
                  createdObjects=6,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Venue=2,
                  Offerer=2)
    provider = Provider.getByClassName('TiteLiveStocks')
    for vp in VenueProvider.query\
                           .filter_by(provider=provider)\
                           .all():
        assert not vp.isActive
        vp.isActive = True
        PcObject.check_and_save(vp)


def test_11_titelive_things_provider(app):
    provider_test(app,
                  TiteLiveThings,
                  None,
                  checkedObjects=422,
                  createdObjects=355,
                  updatedObjects=13,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Thing=355
                 )


def test_12_titelive_thing_thumbs_provider(app):
    provider_test(app,
                  TiteLiveThingThumbs,
                  None,
                  checkedObjects=106,
                  createdObjects=0,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=166,
                  createdThumbs=92,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Thing=0
                 )
    assert db.session.query(func.sum(Thing.thumbCount))\
                         .scalar() == 92


def test_13_titelive_thing_desc_provider(app):
    provider_test(app,
                  TiteLiveThingDescriptions,
                  None,
                  checkedObjects=6,
                  createdObjects=0,
                  updatedObjects=6,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Thing=0
                 )


def test_15_spreadsheet_exp_venues_provider(app):
    provider_test(app,
                  SpreadsheetExpVenues,
                  None,
                  checkedObjects=18,
                  createdObjects=18,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Venue=9,
                  Offerer=9)


def test_16_spreadsheet_exp_stocks_provider(app):
    provider_test(app,
                  SpreadsheetExpStocks,
                  None,
                  checkedObjects=489,
                  createdObjects=489,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Event=7,
                  EventOccurrence=234,
                  Stock=234,
                  Offerer=0,
                  Offer=7,
                  Venue=0
                 )


@pytest.mark.skipif(check_open_agenda_api_is_down(), reason="Open Agenda API is down")
def test_17_openagenda_events_provider(app):
    oa_provider = Provider.getByClassName('OpenAgendaEvents')
    venueProvider = VenueProvider()
    venueProvider.venueId = dehumanize('AE')
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '49050769'
    PcObject.check_and_save(venueProvider)
    venueProvider = VenueProvider.query\
                                 .filter_by(venueIdAtOfferProvider='49050769')\
                                 .one_or_none()
    provider_test(app,
                  OpenAgendaEvents,
                  venueProvider,
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


def test_99_init(app):
    saveCounts(app)
    with app.app_context():
        logger_info = logger.info
        logger.info = lambda o: None
        save_handmade_sandbox()
        logger.info = logger_info
        assertCreatedCounts(app, User=10)
