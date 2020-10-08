from sqlalchemy import Column, Integer

from pcapi.utils.human_ids import humanize
from pcapi.utils.object_storage import get_storage_base_url, build_thumb_path
from pcapi.utils.string_processing import get_model_plural_name


class HasThumbMixin(object):
    thumbCount = Column(Integer(), nullable=False, default=0)

    def get_thumb_storage_id(self, index: int) -> str:
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")
        return build_thumb_path(self, index)

    @property
    def thumbUrl(self):
        if self.thumbCount == 0:
            return None
        base_url = get_storage_base_url()
        thumb_url = base_url + "/thumbs"
        return '{}/{}/{}'.format(thumb_url, get_model_plural_name(self), humanize(self.id))
