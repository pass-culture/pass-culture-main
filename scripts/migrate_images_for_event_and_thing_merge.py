""" move images """
import traceback
from pprint import pprint
from flask import current_app as app

from utils.storage_utils import do_move_images_to_new_folder


@app.manager.option('-c',
                    '--container',
                    help='Container name')
@app.manager.option('-f',
                    '--from-folder',
                    help='Source folder')
@app.manager.option('-t',
                    '--to-folder',
                    help='Destination folder')
def move_images_to_new_folder(container, from_folder, to_folder):
    try:
        do_move_images_to_new_folder(container, from_folder, to_folder)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
