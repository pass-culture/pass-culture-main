""" update providables """
from flask import current_app as app

from local_providers.init_titelive_things import InitTiteLiveThings
from scripts.update_providables import do_update


@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per providerName/venueId'
                         + ' (for test purposes)', type=int)
@app.manager.option('-f',
                    '--file',
                    help='File containing Titelive Things data')
def import_titelive_full_table(limit: int, file: str):
    provider = InitTiteLiveThings(file)
    return do_update(provider, limit)
