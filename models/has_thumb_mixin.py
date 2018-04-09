from colorthief import ColorThief
from flask import current_app as app
from PIL import Image
import requests
import tempfile

from utils.human_ids import humanize
from utils.object_storage import delete_public_object,\
                                 get_public_object_date,\
                                 store_public_object
from utils.string_processing import inflect_engine

db = app.db


class HasThumbMixin(object):
    thumbCount = db.Column(db.Integer(), nullable=False, default=0)
    firstThumbDominantColor = db.Column(db.Binary(3),
                                        db.CheckConstraint('"thumbCount"=0 OR "firstThumbDominantColor" IS NOT NULL',
                                                           name='check_thumb_has_dominant_color'),
                                        nullable=True)

    def delete_thumb(self, index):
        delete_public_object("thumbs", self.thumb_storage_id(index))

    def thumb_date(self, index):
        return get_public_object_date("thumbs", self.thumb_storage_id(index))

    def thumb_storage_id(self, index):
        return inflect_engine.plural(self.__class__.__name__.lower()) + "/"\
                                     + humanize(self.id)\
                                     + (('_' + str(index)) if index > 0 else '')

    def save_thumb(self, thumb, index, image_type=None, dominant_color=None):
        if isinstance(thumb, str):
            if not thumb[0:4] == 'http':
                raise ValueError('Invalid thumb URL for object '
                                 + str(self)
                                 + ' : ' + thumb)
            thumb_response = requests.get(thumb)
            content_type = thumb_response.headers['Content-type']
            if thumb_response.status_code == 200 and\
               content_type.split('/')[0] == 'image':
                thumb = thumb_response.content
                image_type = image_type or content_type.split('/')[1]
            else:
                raise ValueError('Error downloading thumb for object '
                                 + str(self)
                                 + ' status_code: ' + str(thumb_response.status_code) + ', '
                                 + ' content-type: ' + content_type)
        if image_type is None:
            with tempfile.TemporaryFile() as tf:
                tf.write(thumb)
                img = Image.open(tf)
                image_type = img.format.lower()
        if index == 0:
            if dominant_color is None:
                with tempfile.TemporaryFile() as tf:
                    tf.write(thumb)
                    color_thief = ColorThief(tf)
                    dominant_color = bytearray(color_thief.get_color(quality=1))
            self.firstThumbDominantColor = dominant_color
        store_public_object("thumbs",
                            self.thumb_storage_id(index),
                            thumb,
                            "image/" + ('svg+xml'
                                        if image_type == 'svg'
                                        else image_type))
        self.thumbCount = max(index+1, self.thumbCount or 0)


app.model.HasThumbMixin = HasThumbMixin
