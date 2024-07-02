import typing

import factory.alchemy
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.orm

from pcapi import models
from pcapi.models import db


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # See comment in _save()
        # sqlalchemy_session = pcapi.models.db.session
        sqlalchemy_session = "ignored"  # see hack in `_save()`
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _save(
        cls,
        model_class: typing.Type[models.Model],
        session: typing.Any,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Model:
        # pytest-flask-sqlalchemy mocks (replaces) `db.session` to
        # remove the session and rollback changes at the end of each
        # test function (see `_session()` fixture in
        # pytest-flask-sqlalchemy). As such, the session that is used
        # in tests is not the session we defined in
        # `Meta.sqlalchemy_session` above. Because of this, data added
        # through a factory is not rollback'ed. To work around this,
        # here is a hack.

        # This issue is discussed here: https://github.com/jeancochrane/pytest-flask-sqlalchemy/issues/12
        session = db.session

        known_fields = {
            prop.key
            for prop in sqlalchemy.orm.class_mapper(model_class).iterate_properties
            if isinstance(prop, (sqlalchemy.orm.ColumnProperty, sqlalchemy.orm.RelationshipProperty))
        }
        unknown_fields = set(kwargs.keys()) - known_fields
        if unknown_fields:
            raise ValueError(
                f"{cls.__name__} received unexpected argument(s): "
                f"{', '.join(sorted(unknown_fields))}. "
                f"Possible arguments are: {', '.join(sorted(known_fields))}"
            )

        return super()._save(model_class, session, *args, **kwargs)

    @classmethod
    def _get_or_create(
        cls,
        model_class: typing.Type[models.Model],
        session: typing.Any,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Model:
        # See comment in _save for the reason why we inject the
        # session like this.
        session = db.session
        return super()._get_or_create(model_class, session, *args, **kwargs)
