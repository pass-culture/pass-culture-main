""" local providers test """
import subprocess
from inspect import isclass
from glob import glob
from sqlalchemy import func

from local_providers import OpenAgendaEvents,\
                            SpreadsheetExpStocks,\
                            SpreadsheetExpVenues,\
                            TiteLiveThingDescriptions,\
                            TiteLiveThingThumbs,\
                            TiteLiveThings,\
                            TiteLiveStocks,\
                            TiteLiveVenues
import models
from models.db import db
from models.pc_object import PcObject
from models.provider import Provider
from models.thing import Thing
from models.venue_provider import VenueProvider
from utils.config import API_ROOT_PATH
from utils.human_ids import dehumanize
from utils.object_storage import STORAGE_DIR
from utils.test_utils import create_offerer, create_venue, create_thing, create_thing_offer

savedCounts = {}


def saveCounts(app):
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model)\
           and issubclass(model, PcObject)\
           and modelName != "PcObject":
            savedCounts[modelName] = model.query.count()


def assertCreatedCounts(app, **counts):
    for modelName in counts:
        model = getattr(models, modelName)
        assert model.query.count() - savedCounts[modelName]\
               == counts[modelName]


def assertEmptyDb(app):
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isinstance(model, PcObject):
            if modelName == 'Mediation':
                assert model.query.count() == 2
            else:
                assert model.query.count() == 0


def assert_created_thumbs():
    assert len(glob(str(STORAGE_DIR / "thumbs" / "*"))) == 1


def provider_test(app, provider, venueProvider, **counts):
    providerObj = provider(venueProvider, mock=True)
    providerObj.dbObject.isActive = True
    PcObject.check_and_save(providerObj.dbObject)
    saveCounts(app)
    providerObj.updateObjects()
    for countName in ['updatedObjects',
                      'createdObjects',
                      'checkedObjects',
                      'erroredObjects',
                      'createdThumbs',
                      'updatedThumbs',
                      'checkedThumbs',
                      'erroredThumbs']:
        assert getattr(providerObj, countName) == counts[countName]
        del counts[countName]
    assertCreatedCounts(app, **counts)


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


def test_14_titelive_stock_provider(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.check_and_save(venue)

    oa_provider = Provider.getByClassName('TiteLiveThings')
    venueProvider = VenueProvider()
    venueProvider.venue = venue
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '77567146400110'
    PcObject.check_and_save(venueProvider)
    venueProvider = VenueProvider.query \
        .filter_by(venueIdAtOfferProvider='77567146400110') \
        .one_or_none()

    thing = create_thing(id_at_providers='0002730757438')
    offer = create_thing_offer(venue=venue, thing=thing)

    PcObject.check_and_save(thing, offer)
    
    assert venueProvider is not None
    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=5000,
                  createdObjects=1,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=1
                 )

    # venueProvider = VenueProvider.query\
    #                              .filter_by(venueIdAtOfferProvider='2921')\
    #                              .one_or_none()
    # assert venueProvider is not None
    # provider_test(app,
    #               TiteLiveStocks,
    #               venueProvider,
    #               checkedObjects=370,
    #               createdObjects=332,
    #               updatedObjects=0,
    #               erroredObjects=0,
    #               checkedThumbs=0,
    #               createdThumbs=0,
    #               updatedThumbs=0,
    #               erroredThumbs=0,
    #               Offer=166,
    #               Stock=166
    #              )


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
    result = subprocess.run('PYTHONPATH="." python scripts/pc.py sandbox --name=light',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            cwd=API_ROOT_PATH)
    print(result.stdout)
    print(result.stderr)
    assertCreatedCounts(app, User=5)
