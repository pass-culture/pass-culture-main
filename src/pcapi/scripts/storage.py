""" sandbox script """
# -*- coding: utf-8 -*-

from pprint import pprint
import traceback

from flask import current_app as app

from pcapi.utils.storage_utils import do_copy_prod_container_content_to_dest_container
from pcapi.utils.storage_utils import do_delete_file
from pcapi.utils.storage_utils import do_does_file_exist
from pcapi.utils.storage_utils import do_list_content
from pcapi.utils.storage_utils import do_local_backup_prod_container


# FIXME (dbaty): review error handling in this mmodule. Do we really
# want to print here? Should we not use `logger.exception()` instead?

@app.manager.option('-f',
                    '--folder',
                    help='Destination folder name')
def backup_prod_object_storage(folder):
    try:
        do_local_backup_prod_container(folder)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-c',
                    '--container',
                    help='Container name')
def list_content(container):
    try:
        do_list_content(container)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-c',
                    '--container',
                    help='Container name')
@app.manager.option('-f',
                    '--file',
                    help='File name')
def does_file_exist(container, file):
    try:
        do_does_file_exist(container, file)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-c',
                    '--container',
                    help='Container name')
@app.manager.option('-f',
                    '--file',
                    help='File name')
def delete_file(container, file):
    try:
        do_delete_file(container, file)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


@app.manager.option('-c',
                    '--container',
                    help='Container name')
def copy_prod_container_content_to_dest_container(container):
    try:
        do_copy_prod_container_content_to_dest_container(container)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))

