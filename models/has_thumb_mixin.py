""" has thumb mixin """
import io

import requests
from PIL import Image
from colorthief import ColorThief
from sqlalchemy import Binary, CheckConstraint, Column, Integer

from domain.mediations import crop_image
from models.pc_object import PcObject
from utils.human_ids import humanize
from utils.inflect_engine import inflect_engine
from utils.logger import logger
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
            index,
            image_type=None,
            dominant_color=None,
            convert=True,
            crop=None,
            symlink_path=None):

        if isinstance(thumb, str):
            if not thumb[0:4] == 'http':
                raise ValueError('Invalid thumb URL for object %s : %s' % (str(self), thumb))

            thumb_response = requests.get(thumb)
            content_type = thumb_response.headers['Content-type']

            if thumb_response.status_code == 200 and content_type.split('/')[0] == 'image':
                thumb = thumb_response.content
            else:
                raise ValueError('Error downloading thumb for object %s from url %s (status_code : %s)'
                                 % (str(self), thumb, str(thumb_response.status_code)))

        thumb_bytes = None
        if convert:
            thumb_bytes = io.BytesIO(thumb)
            img = Image.open(thumb_bytes)
            img = img.convert('RGB')

            cropped_img = self.crop_image(crop, img)
            resized_img = self.resize_image(cropped_img)

            thumb_bytes.seek(0)
            thumb_bytes = io.BytesIO(thumb)

            new_bytes = io.BytesIO()

            resized_img.save(
                new_bytes,
                format='JPEG',
                quality=90,
                optimize=True,
                progressive=True
            )

            thumb = new_bytes.getvalue()

        if index == 0:
            if dominant_color is None:
                if thumb_bytes is None:
                    thumb_bytes = io.BytesIO(thumb)
                color_thief = ColorThief(thumb_bytes)
                dominant_color = bytearray(color_thief.get_color(quality=1))
            if dominant_color is None:
                print("Warning: could not determine dominant_color for thumb")
                self.firstThumbDominantColor = b'\x00\x00\x00'
            self.firstThumbDominantColor = dominant_color

        store_public_object("thumbs",
                            self.thumb_storage_id(index),
                            thumb,
                            "image/" + (image_type or "jpeg"),
                            symlink_path=symlink_path)
        self.thumbCount = max(index + 1, self.thumbCount or 0)

        PcObject.check_and_save(self)

    def resize_image(self, cropped_img):
        if cropped_img.size[0] > IDEAL_THUMB_WIDTH:
            ratio = cropped_img.size[1] / cropped_img.size[0]
            resized_img = cropped_img.resize(
                [
                    IDEAL_THUMB_WIDTH,
                    int(IDEAL_THUMB_WIDTH * ratio)
                ]
            )
        else:
            resized_img = cropped_img
        return resized_img

    def crop_image(self, crop, image):
        if crop is None:
            return image

        return crop_image(crop[0], crop[1], crop[2], image)