from domain.mediations import compute_dominant_color, DO_NOT_CROP, standardize_image
from models import Product, PcObject
from utils.logger import logger

CONTAINER_PAGE_SIZE = 1000
MAX_CHUNK_SIZE = 100
LAST_FOLDER_ID = '999'


def import_init_titelive_thumbs(connexion, container_name, titelive_thumb_identifier, folder_index='000'):
    folder_processing = 'titelive/images/' + folder_index
    last_object = None
    files_info_in_container = connexion.get_container(container_name,
                                                      prefix=folder_processing,
                                                      limit=CONTAINER_PAGE_SIZE)[1]

    need_to_process_thumbs = True

    products_chunk_to_update = []

    while need_to_process_thumbs:
        if len(files_info_in_container) < CONTAINER_PAGE_SIZE:
            need_to_process_thumbs = False

        for file_data in files_info_in_container:
            if titelive_thumb_identifier in file_data['name']:
                id_at_providers = file_data['name'].split('_')[0].split('/')[-1]
                titelive_folder = file_data['name'].split('_')[0].split('/')[-2]

                logger.info("Parsing folder : %s" % titelive_folder)
                product_to_update = Product.query.filter(Product.idAtProviders == id_at_providers).first()

                if product_to_update:
                    products_chunk_to_update.append(product_to_update)

                    image = connexion.get_object(container_name, file_data['name'])[1]

                    new_image_name = product_to_update.get_thumb_storage_id(product_to_update.thumbCount)
                    product_to_update.thumbCount += 1
                    if product_to_update.thumbCount == 1:
                        product_to_update.firstThumbDominantColor = compute_dominant_color(image)
                    new_thumb = standardize_image(image, DO_NOT_CROP)

                    connexion.put_object(container_name,
                                         'thumbs/' + new_image_name,
                                         contents=new_thumb,
                                         content_type='image/jpeg')
                    connexion.delete_object(container_name, file_data['name'])

                if len(products_chunk_to_update) >= MAX_CHUNK_SIZE:
                    PcObject.save(*products_chunk_to_update)
                    logger.info("Saving 100 objects")

            last_object = file_data['name']

        if folder_processing != LAST_FOLDER_ID:
            folder_processing = increase_folder_to_process_id(folder_processing)
            files_info_in_container = connexion.get_container(container_name,
                                                              prefix=folder_processing,
                                                              limit=CONTAINER_PAGE_SIZE,
                                                              marker=last_object)[1]


def increase_folder_to_process_id(last_folder_processed):
    next_folder_to_process = int(last_folder_processed) + 1
    while len(str(next_folder_to_process)) < 3:
        next_folder_to_process = '0%s' % str(next_folder_to_process)
    return str(next_folder_to_process)
