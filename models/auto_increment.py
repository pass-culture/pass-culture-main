from inspect import isclass
from sqlalchemy import event

from models.db import db
from models.pc_object import PcObject
import models

def get_last_stored_id_of_model(model):
    ids = db.session.query(model.id).all()
    if ids:
        return max(ids)[0]
    return 0

# as we can insert obj in the db with mock object that imposed
# arbitrary ids (ie not regarding to the last incremented id value stored in the db)
# we need to make the model keep listening to what is the last id inserted
# and then make sure to set the autoincrement id value to it
# in order to avoid conflict of ids during insert time
def make_auto_increment_id_clamped_to_last_inserted_object():
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and modelName != "PcObject" \
                and hasattr(model, 'id'):
            @event.listens_for(model, "before_insert")
            def func(mapper, connection, obj):
                last_stored_id = get_last_stored_id_of_model(obj.__class__)
                if obj.id is None:
                    obj.id = last_stored_id + 1
