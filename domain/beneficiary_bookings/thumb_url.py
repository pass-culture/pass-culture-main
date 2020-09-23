from typing import Optional

from utils.human_ids import humanize
from utils.object_storage import get_storage_base_url


class ThumbUrl:
    def __init__(self, identifier: int, model_name: str):
        self.identifier = identifier
        self.model_name = model_name

    @staticmethod
    def for_product(identifier: int):
        return ThumbUrl(identifier, 'products')

    @staticmethod
    def for_mediation(identifier: int):
        return ThumbUrl(identifier, 'mediations')

    def url(self) -> Optional[str]:
        base_url = get_storage_base_url()
        thumb_url = base_url + "/thumbs"
        return '{}/{}/{}'.format(thumb_url, self.model_name, humanize(self.identifier))
