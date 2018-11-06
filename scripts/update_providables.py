""" update providables """
import traceback
from pprint import pprint

from flask import current_app as app

import local_providers
import models
from models import db, Event, Offerer, Stock, Thing, Venue, VenueProvider
from models.db import db


def do_update(provider, limit):
    try:
        provider.updateObjects(limit)
    except Exception as e:
        print('ERROR: '+e.__class__.__name__+' '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-p',
                    '--provider',
                    help='Limit update to this provider name')
@app.manager.option('-m',
                    '--mock',
                    action="store_true",
                    help='Update from mock data or APIs'
                         + ' if this flag is present')
@app.manager.option('-v',
                    '--venue',
                    help='Limit update to this venue id')
@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per provider/venue'
                         + ' (for test purposes)', type=int)
@app.manager.option('-w',
                    '--venueProvider',
                    help='Limit update to this venueProvider')
@app.manager.option('-o',
                    '--objectType',
                    help='Sync only this objectType of object'
                         + ' (stock, thing or venue)')
def update_providables(provider, venue, venueProvider, limit, objectType, mock=False):

    if venueProvider is not None:
        venueProviderObj = VenueProvider.query\
                                                  .filter_by(id=venueProvider)\
                                                  .first()
        provider_class = getattr(local_providers, venueProviderObj.provider.localClass)
        venueProviderProvider = provider_class(venueProviderObj, mock=mock)
        return do_update(venueProviderProvider, limit)

    # order matters ! An item appears later in this list
    # if it requires items named before it
    # For instance, Stocks require Events or Things
    PROVIDABLE_TYPES = [Offerer,
                        Venue,
                        Event,
                        Thing,
                        Stock]
    if not venue:
        if objectType:
            model = getattr(models, objectType.capitalize())
        for providable_type in [model] if objectType else PROVIDABLE_TYPES:
            for provider_name in local_providers.__all__:
                if provider and provider_name != provider:
                    print("Provider " + provider_name + " does not match provider"
                          + " name supplied in command line. Not updating")
                    continue
                provider_type = getattr(local_providers, provider_name)
                if provider_type.identifierRegexp is None\
                   and provider_type.objectType == providable_type:
                    providerObj = provider_type(None, mock=mock)
                    do_update(providerObj, limit)

    venueProviderQuery = VenueProvider.query
    venueProviderObjs = venueProviderQuery.filter_by(id=int(venue))\
                  if venue\
                  else venueProviderQuery.all()
    if objectType:
        model = getattr(models, objectType.capitalize())
    for providable_type in [model] if objectType else PROVIDABLE_TYPES:
        for venueProviderObj in venueProviderObjs:
            db.session.add(venueProviderObj)
            provider_name = venueProviderObj.provider.localClass
            if provider_name is None:
                continue
            provider_type = getattr(local_providers, provider_name)
            if provider and provider_name != provider:
                print("  Provider " + provider_name + " for venue does not match provider name"
                      + " supplied in command line. Not updating.")
                continue
            if provider_type.objectType != providable_type:
                continue
            venueProviderProvider = provider_type(venueProviderObj, mock=mock)
            do_update(venueProviderProvider, limit)
