""" has thumb mixin """

from sqlalchemy import Binary, CheckConstraint, Column, Integer

from connectors.thumb import fetch_image
from domain.mediations import DO_NOT_CROP, standardize_image, compute_dominant_color
from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.inflect_engine import inflect_engine
from utils.object_storage import delete_public_object, \
    get_public_object_date, \
    store_public_object

IDEAL_THUMB_WIDTH = 750


class HasThumbMixin(object):
    thumbCount = Column(Integer(), nullable=False, default=0)
    firstThumbDominantColor = Column(Binary(3),
                                     CheckConstraint('"thumbCount"=0 OR "firstThumbDominantColor" IS NOT NULL',
                                                     name='check_thumb_has_dominant_color'),
                                     nullable=True)

    def delete_thumb(self, index):
        delete_public_object("thumbs", self.thumb_storage_id(index))

    def thumb_date(self, index):
        return get_public_object_date("thumbs", self.thumb_storage_id(index))

    def thumb_storage_id(self, index):
        if self.id is None:
            raise ValueError("Trying to get thumb_storage_id for an unsaved object")
        return inflect_engine.plural(self.__class__.__name__.lower()) + "/" \
               + humanize(self.id) \
               + (('_' + str(index)) if index > 0 else '')

    def save_thumb(
            self,
            thumb,
            image_index,
            image_type=None,
            dominant_color=None,
            convert=True,
            crop=None,
            symlink_path=None
    ):
        new_thumb = thumb

        if isinstance(thumb, str):
            new_thumb = fetch_image(thumb, str(self))

        if convert:
            crop_params = crop if crop is not None else DO_NOT_CROP
            new_thumb = standardize_image(new_thumb, crop_params)

        if image_index == 0:
            if dominant_color:
                self.firstThumbDominantColor = dominant_color
            else:
                self.firstThumbDominantColor = compute_dominant_color(new_thumb)

        store_public_object(
            'thumbs',
            self.thumb_storage_id(image_index),
            new_thumb,
            'image/' + (image_type or 'jpeg'),
            symlink_path=symlink_path
        )

        self.thumbCount = max(image_index + 1, self.thumbCount or 0)

        PcObject.check_and_save(self)
