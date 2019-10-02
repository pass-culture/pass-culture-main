import os
import re
from io import BytesIO
from typing import Callable

import requests

from domain.mediations import compute_dominant_color
from models import Product, PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

OBJECT_STORAGE_URL = os.environ.get('OBJECT_STORAGE_URL')


def _get_product_thumb(uri: str):
    response = requests.get(OBJECT_STORAGE_URL + '/' + uri)

    if response.status_code != 200:
        logger.error(f'[BATCH][PRODUCT THUMB UPDATE] Could not get thumb for uri {uri}')
        return

    return response.content


def process_product_thumb(uri: str, get_product_thumb=_get_product_thumb):
    is_main_thumb = '_' not in uri

    product_thumb = None
    if is_main_thumb:
        product_thumb = get_product_thumb(uri)
        if not product_thumb:
            return

    product_id = _compute_product_id_from_uri(uri)
    product = Product.query.filter_by(id=product_id).first()

    if product:
        main_thumb_was_not_processed = product.thumbCount == 0 and (not is_main_thumb)
        if main_thumb_was_not_processed:
            logger.error(f'[BATCH][PRODUCT THUMB UPDATE] Trying to process secondary thumb when main '
                         f'thumb was not processed for product with id: "{product.id}" / uri: "{uri}"')
            return
        _update_product_thumb(product, product_thumb)
        logger.info(
            f'[BATCH][PRODUCT THUMB UPDATE] Product with id: "{product.id}" / uri: "{uri}" processed successfully')
        return True
    else:
        logger.error(f'[BATCH][PRODUCT THUMB UPDATE] Product not found for id: "{product_id}" / uri: "{uri}"')


def process_file(file_path: str, _process_product_thumb: Callable = process_product_thumb):
    file = open(file_path, mode='r')
    for line in file:
        _process_product_thumb(uri=line)


def _get_first_thumb_dominant_color_from_image(image: bytes) -> bytes:
    bytes_img = BytesIO(image)
    first_thumb_dominant_color = compute_dominant_color(bytes_img.read())
    return first_thumb_dominant_color


def _compute_product_id_from_uri(uri: str) -> int:
    end_of_uri = uri.split('/')[-1]
    human_id = re.sub(r'_[^_]+$', '', end_of_uri)
    return dehumanize(human_id)


def _update_product_thumb(product: Product, product_thumb: bytes):
    product.thumbCount += 1
    if product_thumb:
        product.firstThumbDominantColor = _get_first_thumb_dominant_color_from_image(product_thumb)
    PcObject.save(product)
