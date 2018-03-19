from colorthief import ColorThief
from flask import current_app as app
import tempfile

from utils.human_ids import humanize
from utils.object_storage import delete_public_object,\
                                 get_public_object_date,\
                                 store_public_object
from utils.string_processing import inflect_engine

db = app.db


class HasThumbMixin(object):
    thumbCount = db.Column(db.Integer(), nullable=False, default=0)
    firstThumbDominantColor = db.Column(db.Binary(3), nullable=True)

    def delete_thumb(self, index):
        delete_public_object("thumbs", self.thumb_storage_id(index))

    def thumb_date(self, index):
        return get_public_object_date("thumbs", self.thumb_storage_id(index))

    def thumb_storage_id(self, index):
        return inflect_engine.plural(self.__class__.__name__.lower()) + "/"\
                                     + humanize(self.id)\
                                     + (('_' + str(index)) if index > 0 else '')

    def save_thumb(self, thumb, index):
        with tempfile.TemporaryFile() as tf:
            tf.write(thumb)
            color_thief = ColorThief(tf)
            self.firstThumbDominantColor = bytearray(color_thief.get_color(quality=1))
        store_public_object("thumbs",
                            self.thumb_storage_id(index),
                            thumb,
                            "image/jpeg")
        self.thumbCount = max(index+1, self.thumbCount or 0)


app.model.HasThumbMixin = HasThumbMixin
