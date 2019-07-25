""" copy_pro_storage """
from utils.storage_utils import do_copy_prod_container_content_to_dest_container


def copy_prod_storage():
    testing_destination_storage = "storage-pc-dev"
    do_copy_prod_container_content_to_dest_container(testing_destination_storage)

    staging_destination_storage = "storage-pc-staging"
    do_copy_prod_container_content_to_dest_container(staging_destination_storage)


copy_prod_storage()