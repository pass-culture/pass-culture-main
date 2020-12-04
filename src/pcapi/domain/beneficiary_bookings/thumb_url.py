from typing import Optional

from pcapi import settings
from pcapi.utils.human_ids import humanize


class ThumbUrl:
    def __init__(self, identifier: int, model_name: str):
        self.identifier = identifier
        self.model_name = model_name

    @staticmethod
    def for_product(identifier: int):
        return ThumbUrl(identifier, "products")

    @staticmethod
    def for_mediation(identifier: int):
        return ThumbUrl(identifier, "mediations")

    # TODO: merge this with HasThumbMixin.thumbUrl ?
    def url(self) -> Optional[str]:
        thumb_url = settings.OBJECT_STORAGE_URL + "/thumbs"
        return "{}/{}/{}".format(thumb_url, self.model_name, humanize(self.identifier))
