import sqlalchemy.orm as sa_orm
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.orm import declarative_mixin

from pcapi import settings
from pcapi.utils.human_ids import humanize


@declarative_mixin
class HasThumbMixin:
    # Let mypy know that classes that use this mixin have an id
    # (possibly through another mixin), and that this mixin can use it
    # in its own functions.
    id: sa_orm.Mapped[int]

    thumbCount: sa_orm.Mapped[int] = Column(Integer(), nullable=False, default=0)

    @property
    def thumb_path_component(self) -> str:
        """Return the part of the externally-stored file path that depends on
        the type of the model.

        Example: "products", "mediations", etc.

        Must be implemented by classes that use this mixin.
        """
        raise NotImplementedError()

    def get_thumb_storage_id(self, suffix_str: str = "", ignore_thumb_count: bool = False) -> str:
        """
        Used when uploading a thumb.
        The thumbCount must be incremented before calling this function.
        It is by default based on the thumbCount, but a specific `suffix_str` can be used.
        For example, a Venue uses a timestamp.
        Also, ignore_thumb_count can be set to True to specifically ignore the thumb_count
        """
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")

        if suffix_str:
            return f"{self.thumb_path_component}/{humanize(self.id)}_{suffix_str}"

        return f"{self.thumb_path_component}/{humanize(self.id)}{self.get_thumb_storage_id_suffix(ignore_thumb_count)}"

    def get_thumb_storage_id_suffix(self, ignore_thumb_count: bool = False) -> str:
        """
        To keep compatibility with all the already uploaded assets, we use "" instead of "_0" for the first thumb
        """
        if ignore_thumb_count or self.thumbCount == 1:
            return ""

        if self.thumbCount < 1:
            raise ValueError("This object has no thumb")

        return f"_{self.thumbCount - 1}"

    @property
    def thumb_base_url(self) -> str:
        return settings.OBJECT_STORAGE_URL + "/thumbs"

    @property
    def thumbUrl(self) -> str | None:
        """
        Build the url where to read a thumb
        Override if the thumb is uploaded to a customized storage id
        """
        assert hasattr(self, "id")  # helps mypy
        if self.thumbCount == 0:
            return None

        return (
            f"{self.thumb_base_url}/{self.thumb_path_component}/{humanize(self.id)}{self.get_thumb_storage_id_suffix()}"
        )
