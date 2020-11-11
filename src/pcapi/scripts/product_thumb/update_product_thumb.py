import os
import re
from typing import Callable
from typing import List
from typing import Optional

import requests

from pcapi.models import Product
from pcapi.scripts.performance_toolkit import CHUNK_SIZE
from pcapi.scripts.performance_toolkit import bulk_update_pc_objects
from pcapi.scripts.performance_toolkit import get_pc_object_by_id_in_database
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.logger import logger


OBJECT_STORAGE_URL = os.environ.get("OBJECT_STORAGE_URL")


def _get_product_thumb(uri: str) -> Optional[bytes]:
    thumb_storage_url = os.path.join(OBJECT_STORAGE_URL, uri)
    response = requests.get(thumb_storage_url)

    if response.status_code != 200:
        logger.error(f"[BATCH][PRODUCT THUMB UPDATE] Could not get thumb for uri {uri}")
        return

    return response.content


def process_product_thumb(uri: str, get_product_thumb: Callable = _get_product_thumb) -> Optional[bool]:
    is_main_thumb = "_" not in uri

    if is_main_thumb:
        product_thumb = get_product_thumb(uri)
        if not product_thumb:
            return

    product_id = _compute_product_id_from_uri(uri)
    product = get_pc_object_by_id_in_database(product_id, Product)

    if product:
        main_thumb_was_not_processed = product.thumbCount == 0 and (not is_main_thumb)
        if main_thumb_was_not_processed:
            return

        product.thumbCount += 1
        return product

    else:
        return None


def process_file(file_path: str, _process_product_thumb: Callable = process_product_thumb):
    lines = _get_lines_from_file(file_path)
    lines_count = len(lines)
    logger.info(f"[BATCH][PRODUCT THUMB UPDATE] Thumbs to process {lines_count}")

    products_to_save = []
    for index, line in enumerate(lines):
        uri = line.strip()
        product_to_save = _process_product_thumb(uri=uri)
        if product_to_save:
            products_to_save.append(product_to_save)

        if len(products_to_save) % CHUNK_SIZE == 0:
            bulk_update_pc_objects(products_to_save, Product)
            logger.info(f"[BATCH][PRODUCT THUMB UPDATE] Progress {round(index / lines_count * 100, 3)}")
            products_to_save = []

    if len(products_to_save) > 0:
        bulk_update_pc_objects(products_to_save, Product)
    logger.info(f"[BATCH][PRODUCT THUMB UPDATE] END")


def _get_lines_from_file(file_path: str) -> List[str]:
    lines = []
    with open(file_path, mode="r") as file_lines:
        for line in file_lines:
            lines.append(line.strip())
    return lines


def _compute_product_id_from_uri(uri: str) -> int:
    last_uri_chunk = uri.split("/")[-1]
    characters_after_underscore = r"_[^_]+$"
    human_id = re.sub(characters_after_underscore, "", last_uri_chunk)
    return dehumanize(human_id)
