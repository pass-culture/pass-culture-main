from sqlalchemy import Column, Integer

from utils.human_ids import humanize
from utils.object_storage import delete_public_object, \
    get_public_object_date, \
    get_storage_base_url, \
    build_thumb_path
from utils.string_processing import get_model_plural_name


class HasThumbMixin(object):
    thumbCount = Column(Integer(), nullable=False, default=0)

    def delete_thumb(self, index):
        delete_public_object("thumbs", self.get_thumb_storage_id(index))

    def thumb_date(self, index):
        return get_public_object_date("thumbs", self.get_thumb_storage_id(index))

    def get_thumb_storage_id(self, index: int) -> str:
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")
        return build_thumb_path(self, index)

    @property
    def thumbUrl(self):
        base_url = get_storage_base_url()
        thumb_url = base_url + "/thumbs"
        return '{}/{}/{}'.format(thumb_url, get_model_plural_name(self), humanize(self.id))
