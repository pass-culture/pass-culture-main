from sqlalchemy import Column
from sqlalchemy import Integer

from pcapi import settings
from pcapi.utils.human_ids import humanize


class HasThumbMixin:
    thumbCount = Column(Integer(), nullable=False, default=0)

    @property
    def thumb_path_component(self):
        """Return the part of the externally-stored file path that depends on
        the type of the model.

        Example: "products", "mediations", etc.

        Must be implemented by classes that use this mixin.
        """
        raise NotImplementedError()

    def get_thumb_storage_id(self, index: int) -> str:
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")
        suffix = f"_{index}" if index > 0 else ""
        return f"{self.thumb_path_component}/{humanize(self.id)}{suffix}"

    @property
    def thumb_base_url(self):
        return settings.OBJECT_STORAGE_URL + "/thumbs"

    @property
    def thumbUrl(self):
        if self.thumbCount == 0:
            return None
        return "{}/{}/{}".format(self.thumb_base_url, self.thumb_path_component, humanize(self.id))
