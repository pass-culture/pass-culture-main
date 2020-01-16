""" sandbox script """
# -*- coding: utf-8 -*-

import traceback
from pprint import pprint

from flask import current_app as app

from utils.storage_utils import do_list_content, \
    do_does_file_exist, \
    do_delete_file, \
    do_copy_prod_container_content_to_dest_container, \
    do_local_backup_prod_container


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

