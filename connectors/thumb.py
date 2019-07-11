import requests

" has thumb mixin """

from domain.mediations import DO_NOT_CROP, standardize_image, compute_dominant_color
from models import ApiErrors
from models.pc_object import PcObject
from utils.logger import logger
from utils.object_storage import store_public_object


def fetch_image(thumb_url: str, target_object: str) -> bytes:
    if not thumb_url[0:4] == 'http':
        raise ValueError('Invalid thumb URL for object %s : %s' % (target_object, thumb_url))

    response = requests.get(thumb_url)
    content_type = response.headers['Content-type']
    is_an_image = content_type.split('/')[0] == 'image'

    if response.status_code == 200 and is_an_image:
        return response.content
    else:
        raise ValueError(
            'Error downloading thumb for object %s from url %s (status_code : %s)'
            % (target_object, thumb_url, str(response.status_code)))


def save_thumb(
        model_with_thumb,
        thumb,
        image_index,
        image_type=None,
        dominant_color=None,
        convert=True,
        crop=None,
        symlink_path=None,
        need_save=True
):
    new_thumb = thumb

    if isinstance(thumb, str):
        try:
            new_thumb = fetch_image(thumb, str(model_with_thumb))
        except ValueError as e:
            logger.error(e)
            raise ApiErrors({'thumbUrl': ["L'adresse saisie n'est pas valide"]})

    if convert:
        crop_params = crop if crop is not None else DO_NOT_CROP
        new_thumb = standardize_image(new_thumb, crop_params)

    if image_index == 0:
        if dominant_color:
            model_with_thumb.firstThumbDominantColor = dominant_color
        else:
            model_with_thumb.firstThumbDominantColor = compute_dominant_color(new_thumb)

    store_public_object(
        'thumbs',
        model_with_thumb.get_thumb_storage_id(image_index),
        new_thumb,
        'image/' + (image_type or 'jpeg'),
        symlink_path=symlink_path
    )

    model_with_thumb.thumbCount = model_with_thumb.thumbCount + 1

    if need_save:
        PcObject.save(model_with_thumb)
