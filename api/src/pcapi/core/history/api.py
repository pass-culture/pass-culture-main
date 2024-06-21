import decimal
import enum
import math
import typing

from sqlalchemy.ext.mutable import MutableDict

from pcapi.core.finance import models as finance_models
from pcapi.core.history import models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models import db


def add_action(
    action_type: models.ActionType,
    author: users_models.User | None,
    user: users_models.User | None = None,
    offerer: offerers_models.Offerer | None = None,
    venue: offerers_models.Venue | None = None,
    finance_incident: finance_models.FinanceIncident | None = None,
    bank_account: finance_models.BankAccount | None = None,
    rule: offers_models.OfferValidationRule | None = None,
    comment: str | None = None,
    **extra_data: typing.Any,
) -> models.ActionHistory:
    legit_actions = (
        models.ActionType.BLACKLIST_DOMAIN_NAME,
        models.ActionType.REMOVE_BLACKLISTED_DOMAIN_NAME,
        models.ActionType.ROLE_PERMISSIONS_CHANGED,
    )
    if not any((user, offerer, venue, finance_incident, bank_account, rule)) and (action_type not in legit_actions):
        raise ValueError("No resource (user, offerer, venue, finance incident, bank account, rule)")

    # author/user/offerer/venue/bank_account object and its would may not be associated before flush() or commit()
    db.session.flush()

    if user is not None and user.id is None:
        raise RuntimeError("Unsaved user would be saved with action: %s" % (user.email,))

    if offerer is not None and offerer.id is None:
        raise RuntimeError("Unsaved offerer would be saved with action: %s" % (offerer.name,))

    if venue is not None and venue.id is None:
        raise RuntimeError("Unsaved venue would be saved with action %s" % (venue.name,))

    if bank_account is not None and bank_account.id is None:
        raise RuntimeError("Unsaved bank account would be saved with action %s" % bank_account.label)

    if rule is not None and rule.id is None:
        raise RuntimeError("Unsaved rule would be saved with action %s" % rule.name)

    if not isinstance(author, users_models.User):
        # None or AnonymousUserMixin
        # Examples: offerer validated by token (without authentication), offerer created by script
        author = None

    action = models.ActionHistory(
        actionType=action_type,
        authorUser=author.real_user if author else None,
        user=user,
        # FIXME remove type ignores when upgrading to sqlalchemy 2.0
        offerer=offerer,  # type: ignore[arg-type]
        venue=venue,  # type: ignore[arg-type]
        financeIncident=finance_incident,  # type: ignore[arg-type]
        bankAccount=bank_account,  # type: ignore[arg-type]
        rule=rule,  # type: ignore[arg-type]
        comment=comment or None,  # do not store empty string
        extraData=extra_data,
    )

    db.session.add(action)

    return action


class ObjectUpdateSnapshot:
    def __init__(self, obj: Model, author: users_models.User) -> None:
        self.snapshot = UpdateSnapshot()
        self.obj = obj
        self.author = author
        self.add_action_target = {obj.__class__.__tablename__: obj}

    def set(self, field_name: str, old: typing.Any, new: typing.Any) -> "ObjectUpdateSnapshot":
        """
        Add a single field update to the update snapshot.
        """
        self.snapshot.set(field_name, old, new)
        return self

    def _is_different(self, field_name: str, old_value: typing.Any, new_value: typing.Any) -> bool:
        if field_name in ("latitude", "longitude"):
            # Avoid diff: "Latitude : 46.66979 => 46.669789" because of different precision in API and db storage
            return not math.isclose(float(old_value), float(new_value), rel_tol=0.00001)

        return old_value != new_value

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

            field_name = field_name_template.format(column)
            if self._is_different(field_name, old_value, new_value):
                self.snapshot.set(field_name, old=old_value, new=new_value)

        return self

    def to_dict(self) -> typing.Mapping[str, typing.Any]:
        return self.snapshot.to_dict()

    @property
    def is_empty(self) -> bool:
        return self.snapshot.is_empty

    def add_action(self) -> models.ActionHistory | None:
        if self.is_empty:
            return None

        return add_action(
            models.ActionType.INFO_MODIFIED,
            self.author,
            **self.add_action_target,
            modified_info=self.to_dict(),
        )


class UpdateSnapshot:
    """
    Use UpdateSnapshot when model update needs to be tracked and logged
    through add_action's extraData parameter.

    Its simple interface helps tracking and formatting those
    information, as expected. No need to worry whether the key is old,
    old_info, etc.
    """

    def __init__(self) -> None:
        self._fields: typing.MutableMapping[str, typing.Any] = {}

    def set(self, field_name: str, old: typing.Any, new: typing.Any) -> None:
        if old in ("", {}, []):
            old = None
        if new in ("", {}, []):
            new = None
        if old != new:
            self._fields[field_name] = {"old_info": old, "new_info": new}

    def to_dict(self) -> typing.Mapping[str, typing.Any]:
        return serialize_fields(self._fields)

    @property
    def is_empty(self) -> bool:
        return not self._fields


def _serialize_value(data: typing.Any) -> typing.Any:
    # Warning: str is a Collection
    if data is None or isinstance(data, (bool, int, str)):
        return data
    if isinstance(data, enum.Enum):
        return data.value
    if isinstance(data, typing.Mapping):
        return serialize_fields(data)
    if isinstance(data, typing.Collection):
        return list(serialize_collection(data))
    return str(data)


def serialize_fields(fields: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, typing.Any]:
    res: typing.MutableMapping[str, typing.Any] = {}

    for column, data in fields.items():
        res[column] = _serialize_value(data)

    return res


def serialize_collection(items: typing.Collection) -> typing.Collection:
    res: list[typing.Any] = []

    for item in items:
        serialized_item = _serialize_value(item)
        if isinstance(serialized_item, list):
            res.extend(serialized_item)
        else:
            res.append(serialized_item)

    return res
