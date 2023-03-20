import decimal
import enum
import typing

from sqlalchemy.ext.mutable import MutableDict

from pcapi.core.history import models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.repository import repository


def log_action(
    action_type: models.ActionType,
    author: users_models.User | None,
    user: users_models.User | None = None,
    offerer: offerers_models.Offerer | None = None,
    venue: offerers_models.Venue | None = None,
    comment: str | None = None,
    save: bool = True,
    **extra_data: typing.Any,
) -> models.ActionHistory:
    """
    Set save parameter to False if you want to save the returned object at the same time as modified resources.

    Be careful: author/user/offerer/venue object and its id may not be associated before the action is saved and/or
    before the new object itself is inserted in the database. RuntimeError are issued in case this function would save
    new resources in parameters; when such an exception is raised, it shows a bug in our code.
    """
    if (not user and not offerer and not venue) and (action_type != models.ActionType.BLACKLIST_DOMAIN_NAME):
        raise ValueError("No resource (user, offerer, venue)")

    if save:
        if user is not None and user.id is None:
            raise RuntimeError("Unsaved user would be saved with action: %s" % (user.email,))

        if offerer is not None and offerer.id is None:
            raise RuntimeError("Unsaved offerer would be saved with action: %s" % (offerer.name,))

        if venue is not None and venue.id is None:
            raise RuntimeError("Unsaved venue would be saved with action %s" % (venue.name,))

    if not isinstance(author, users_models.User):
        # None or AnonymousUserMixin
        # Examples: offerer validated by token (without authentication), offerer created by script
        author = None

    action = models.ActionHistory(
        actionType=action_type,
        authorUser=author,
        user=user,
        # FIXME remove type ignores when upgrading to sqlalchemy 2.0
        offerer=offerer,  # type: ignore
        venue=venue,  # type: ignore
        comment=comment or None,  # do not store empty string
        extraData=extra_data,
    )

    if save:
        repository.save(action)

    return action


class ObjectUpdateSnapshot:
    def __init__(self, obj: Model, author: users_models.User) -> None:
        self.snapshot = UpdateSnapshot()
        self.obj = obj
        self.author = author
        self.log_action_target = {obj.__class__.__tablename__: obj}

    def set(self, field_name: str, old: typing.Any, new: typing.Any) -> "ObjectUpdateSnapshot":
        """
        Add a single field update to the update snapshot.
        """
        self.snapshot.set(field_name, old, new)
        return self

    def trace_update(
        self,
        data: typing.Mapping,
        target: typing.Any | None = None,
        field_name_template: str = "{}",
        filter_fields: bool = False,
    ) -> "ObjectUpdateSnapshot":
        """
        Add multiple updates to the snapshot, at once: iterate over
        data and for each field that has a different value from the
        target, add it to the current update snapshot.

        Args:
            * data: fields and their new values. eg.
              {"name": "new name"}
            * target: the traced object (usually self.obj but it can
              also be a relation, eg. venue.contact)
            * field_name_template: template string used to build the
              field name inside the history object. By default, it will
              be the column name. Can only have one placeholder, for the
              column name.
            * filter_fields: if true, ignore fields that are not
              recognized. Note that if false, getattr(target, column)
              will raise an error.
        """
        if not target:
            target = self.obj

        if filter_fields:
            data = {column: new_value for column, new_value in data.items() if hasattr(target, column)}

        for column, new_value in data.items():
            if isinstance(getattr(target, column), enum.Enum):
                old_value = getattr(target, column).name
            elif isinstance(getattr(target, column), decimal.Decimal):
                old_value = float(getattr(target, column))
            elif isinstance(getattr(target, column), MutableDict) and new_value is None:
                old_value = None
            else:
                old_value = getattr(target, column)

            if old_value != new_value:
                field_name = field_name_template.format(column)
                self.snapshot.set(field_name, old=old_value, new=new_value)

        return self

    def to_dict(self) -> typing.Mapping[str, typing.Any]:
        return self.snapshot.to_dict()

    def log_update(self, save: bool = False) -> models.ActionHistory | None:
        modified_info = self.to_dict()
        if not modified_info:
            return None

        return log_action(
            models.ActionType.INFO_MODIFIED,
            self.author,
            **self.log_action_target,
            modified_info=modified_info,
            save=save,
        )


class UpdateSnapshot:
    """
    Use UpdateSnapshot when model update needs to be tracked and logged
    through log_action's extraData parameter.

    Its simple interface helps tracking and formatting those
    information, as expected. No need to worry whether the key is old,
    old_info, etc.
    """

    def __init__(self) -> None:
        self._fields: typing.MutableMapping[str, typing.Any] = {}

    def set(self, field_name: str, old: typing.Any, new: typing.Any) -> None:
        self._fields[field_name] = {"old_info": old, "new_info": new}

    def to_dict(self) -> typing.Mapping[str, typing.Any]:
        return serialize_fields(self._fields)


def serialize_fields(fields: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
    res: typing.MutableMapping[str, typing.Any] = {}

    for column, data in fields.items():
        if isinstance(data, str):  # str is a Collection
            res[column] = data
        elif isinstance(data, typing.Mapping):
            res[column] = serialize_fields(data)
        elif isinstance(data, typing.Collection):
            res[column] = list(serialize_collection(data))
        else:
            res[column] = str(data)

    return res


def serialize_collection(items: typing.Collection) -> typing.Collection:
    res: list[typing.Any] = []

    for item in items:
        if isinstance(item, str):  # str is a Collection
            res.append(item)
        elif isinstance(item, typing.Mapping):
            res.append(serialize_fields(item))
        elif isinstance(item, typing.Collection):
            res.extend(serialize_collection(item))
        else:
            res.append(str(item))

    return res
