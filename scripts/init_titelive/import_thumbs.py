from domain.mediations import compute_dominant_color
from models import Thing, PcObject


def import_init_titelive_thumbs(connexion, container_name, titelive_thumb_identifier):
    images_in_object_storage = get_titelive_thumb_names_group_by_id_at_providers(connexion,
                                                                                 container_name,
                                                                                 titelive_thumb_identifier)

    existing_things_from_providers = Thing.query \
        .filter(Thing.idAtProviders != None) \
        .all()

    for thing in existing_things_from_providers:
        if thing.idAtProviders in images_in_object_storage:
            for existing_image_name in images_in_object_storage[thing.idAtProviders]:
                image = connexion.get_object(container_name,
                                             existing_image_name)
                new_image_name = thing.thumb_storage_id(thing.thumbCount)
                thing.thumbCount += 1
                if thing.thumbCount == 1:
                    thing.firstThumbDominantColor = compute_dominant_color(image[1])
                connexion.put_object(container_name,
                                     'thumbs/' + new_image_name,
                                     contents=image[1],
                                     content_type='image/jpeg')
                connexion.delete_object(container_name,
                                        existing_image_name)
            PcObject.check_and_save(thing)
    return new_image_name


def get_titelive_thumb_names_group_by_id_at_providers(connexion, container_name, titelive_thumb_identifier):
    images_in_object_storage = {}
    for data in connexion.get_container(container_name)[1]:
        if titelive_thumb_identifier in data['name']:
            id_at_providers = data['name'].split('_')[0].split('/')[-1]
            if id_at_providers in images_in_object_storage:
                images_in_object_storage[id_at_providers].append(data['name'])
            else:
                images_in_object_storage[id_at_providers] = [data['name']]
    return images_in_object_storage
