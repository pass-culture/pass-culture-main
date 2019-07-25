""" backup_prod_storage """
import os

from utils.storage_utils import do_local_backup_prod_container


def backup_prod_storage():
    destination_folder = os.environ.get("STORAGE_BACKUP_FOLDER")
    do_local_backup_prod_container(destination_folder)


backup_prod_storage()
