from utils.logger import logger
from utils.object_storage import swift_con


def clean_remaining_titelive_images_in_object_storage(container_name, file_pattern):
    connexion = swift_con(container_name)
    for data in connexion.get_container(container_name)[1]:
        if file_pattern in data['name']:
            connexion.delete_object(container_name,
                                    data['name'])
            logger.info("Deleting file : %s" % data['name'])
