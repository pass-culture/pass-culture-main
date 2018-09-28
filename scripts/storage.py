""" sandbox script """
# -*- coding: utf-8 -*-

from pprint import pprint
import traceback
from flask import current_app as app

from utils.storage_utils import do_list_content


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
#
#
# @app.manager.option('-n',
#                     '--name',
#                     help='Container name')
# @app.manager.option('-f',
#                     '--file',
#                     help='File name')
# def delete_file(container_name, file_name):
#     try:
#         delete_file(container_name, file_name)
#     except Exception as e:
#         print('ERROR: ' + str(e))
#         traceback.print_tb(e.__traceback__)
#         pprint(vars(e))