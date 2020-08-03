from abc import abstractmethod, ABC
from typing import Optional

from utils.human_ids import humanize
from utils.object_storage import get_storage_base_url


class ThumbUrl(ABC):
    @staticmethod
    def storage_base_url():
        return get_storage_base_url()

    @abstractmethod
    def url(self) -> Optional[str]:
        pass


class ProductThumbUrl(ThumbUrl):
    def __init__(self, identifier: int):
        self.identifier = identifier
        self.model_name = 'products'

    def url(self) -> Optional[str]:
        base_url = get_storage_base_url()
        thumb_url = base_url + "/thumbs"
        return '{}/{}/{}'.format(thumb_url, self.model_name, humanize(self.identifier))


class MediationThumbUrl(ThumbUrl):
    def __init__(self, identifier: int):
        self.identifier = identifier
        self.model_name = 'mediations'

    def url(self) -> Optional[str]:
        base_url = get_storage_base_url()
        thumb_url = base_url + "/thumbs"
        return '{}/{}/{}'.format(thumb_url, self.model_name, humanize(self.identifier))
