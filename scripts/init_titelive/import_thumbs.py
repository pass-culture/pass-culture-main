from domain.mediations import compute_dominant_color, DO_NOT_CROP, standardize_image
from models import Product, PcObject

CONTAINER_PAGE_SIZE = 1000


def import_init_titelive_thumbs(connexion, container_name, titelive_thumb_identifier):
    last_object = None
    files_info_in_container = connexion.get_container(container_name, limit=CONTAINER_PAGE_SIZE)[1]

    need_to_process_thumbs = True

    while need_to_process_thumbs:
        if len(files_info_in_container) < CONTAINER_PAGE_SIZE:
            need_to_process_thumbs = False

        for file_data in files_info_in_container:
            if titelive_thumb_identifier in file_data['name']:
                id_at_providers = file_data['name'].split('_')[0].split('/')[-1]

                product_to_update = Product.query.filter(Product.idAtProviders == id_at_providers).first()
                if product_to_update:
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
                    print("Product update %s" % str(product_to_update.id))
                    PcObject.save(product_to_update)
                    need_to_process_thumbs = False

            last_object = file_data['name']

        files_info_in_container = connexion.get_container(container_name,
                                                          limit=CONTAINER_PAGE_SIZE,
                                                          marker=last_object)[1]
