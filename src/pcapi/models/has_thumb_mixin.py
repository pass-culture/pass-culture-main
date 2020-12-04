from sqlalchemy import Column
from sqlalchemy import Integer

from pcapi import settings
from pcapi.utils.human_ids import humanize
from pcapi.utils.object_storage import build_thumb_path
from pcapi.utils.string_processing import get_model_plural_name


class HasThumbMixin:
    thumbCount = Column(Integer(), nullable=False, default=0)

    def get_thumb_storage_id(self, index: int) -> str:
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")
        return build_thumb_path(self, index)

    @property
    def thumbUrl(self):
        if self.thumbCount == 0:
            return None
        thumb_url = settings.OBJECT_STORAGE_URL + "/thumbs"
        return "{}/{}/{}".format(thumb_url, get_model_plural_name(self), humanize(self.id))
