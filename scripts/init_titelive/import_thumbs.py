from domain.mediations import compute_dominant_color, DO_NOT_CROP, standardize_image
from models import Product, PcObject


def import_init_titelive_thumbs(connexion, container_name, titelive_thumb_identifier):
    image_names_in_object_storage = get_titelive_thumb_names_group_by_id_at_providers(connexion,
                                                                                      container_name,
                                                                                      titelive_thumb_identifier)
    new_image_name = None
    existing_things_from_providers = Product.query \
        .filter(Product.idAtProviders != None)

    for thing in existing_things_from_providers:
        if thing.idAtProviders in image_names_in_object_storage:
            for existing_image_name in image_names_in_object_storage[thing.idAtProviders]:
                image = connexion.get_object(container_name, existing_image_name)[1]
                new_image_name = thing.get_thumb_storage_id(thing.thumbCount)
                thing.thumbCount += 1
                if thing.thumbCount == 1:
                    thing.firstThumbDominantColor = compute_dominant_color(image)
                new_thumb = standardize_image(image, DO_NOT_CROP)
                connexion.put_object(container_name,
                                     'thumbs/' + new_image_name,
                                     contents=new_thumb,
                                     content_type='image/jpeg')
                connexion.delete_object(container_name,
                                        existing_image_name)
            PcObject.check_and_save(thing)
    return new_image_name


def get_titelive_thumb_names_group_by_id_at_providers(connexion, container_name, titelive_thumb_identifier):
    images_in_object_storage = {}
    files_info_in_container = connexion.get_container(container_name)[1]
    for file_data in files_info_in_container:
        if titelive_thumb_identifier in file_data['name']:
            id_at_providers = file_data['name'].split('_')[0].split('/')[-1]
            if id_at_providers in images_in_object_storage:
                images_in_object_storage[id_at_providers].append(file_data['name'])
            else:
                images_in_object_storage[id_at_providers] = [file_data['name']]
    return images_in_object_storage
