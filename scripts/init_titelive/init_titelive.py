""" update providables """
import traceback
from pprint import pprint

from flask import current_app as app

from local_providers.init_titelive_thing_descriptions import InitTiteLiveThingDescriptions
from local_providers.init_titelive_things import InitTiteLiveThings
from scripts.init_titelive.clean_images_in_object_storage import clean_remaining_titelive_images_in_object_storage
from scripts.init_titelive.import_thumbs import import_init_titelive_thumbs
from scripts.update_providables import do_update
from utils.storage_utils import swift_con


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


@app.manager.option('-c',
                    '--container',
                    help='Object storage container name')
@app.manager.option('-p',
                    '--pattern',
                    help='Titelive thumbs pattern for imported images')
def import_titelive_full_thumbs(container, pattern):
    try:
        connexion = swift_con(container)
        import_init_titelive_thumbs(connexion, container, pattern)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-c',
                    '--container',
                    help='Object storage container name')
@app.manager.option('-p',
                    '--pattern',
                    help='Titelive images pattern for imported images')
def clean_titelive_remaining_images(container, pattern):
    try:
        clean_remaining_titelive_images_in_object_storage(container, pattern)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per providerName/venueId'
                         + ' (for test purposes)', type=int)
@app.manager.option('-f',
                    '--file',
                    help='File containing Titelive Description Things data')
def import_titelive_full_descriptions(limit: int, file: str):
    provider = InitTiteLiveThingDescriptions(file)
    return do_update(provider, limit)
