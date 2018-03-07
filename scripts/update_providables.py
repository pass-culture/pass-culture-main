from flask import current_app as app
from pprint import pprint
import traceback


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
@app.manager.option('-o',
                    '--offerer',
                    help='Limit update to this offerer id')
@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per provider/offerer'
                         + ' (for test purposes)', type=int)
@app.manager.option('-t',
                    '--type',
                    help='Sync only this type of object'
                         + ' (offer, thing or offerer)')
def update_providables(provider, offerer, limit, type, mock=False):

    # order matters ! An item appears later in this list
    # if it requires items named before it
    # For instance, Offers require Events or Things
    PROVIDABLE_TYPES = [app.model.Offerer,
                        app.model.Venue,
                        app.model.Event,
                        app.model.Thing,
                        app.model.Offer]
    if not offerer:
        for providable_type in [app.model[type.capitalize()]]\
                               if type else PROVIDABLE_TYPES:
            for provider_name in app.local_providers:
                if provider and provider_name != provider:
                    print("  Provider " + provider_name + " does not match provider"
                          + " name supplied in command line. Not updating")
                    continue
                provider_type = app.local_providers[provider_name]
                if provider_type.identifierRegexp is None\
                   and provider_type.objectType == providable_type:
                    providerObj = provider_type(None, mock=mock)
                    do_update(providerObj, limit)

    offererProviderQuery = app.model.OffererProvider.query
    offererProviderObjs = offererProviderQuery.filter_by(id=int(offerer))\
                  if offerer\
                  else offererProviderQuery.all()
    for providable_type in [app.model[type.capitalize()]]\
                           if type else PROVIDABLE_TYPES:
        for offererProviderObj in offererProviderObjs:
            app.db.session.add(offererProviderObj)
            provider_name = offererProviderObj.provider.localClass
            if provider_name is None:
                continue
            provider_type = app.local_providers[provider_name]
            if provider and provider_name != provider:
                print("  Provider " + provider_name + " for offerer does not match provider name"
                      + " supplied in command line. Not updating.")
                continue
            if provider_type.objectType != providable_type:
                continue
            offererProvider = provider_type(offererProviderObj, mock=mock)
            do_update(offererProvider, limit)
