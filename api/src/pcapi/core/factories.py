import typing

import factory.alchemy

from pcapi.models import db


class BaseFactory[T](factory.alchemy.SQLAlchemyModelFactory):
    """
    When defining a factory, you can write

    class MyFactory(BaseFactory[MyModel]):
        class Meta:
            model = MyModel

    This way, MyFactory(), MyFactory.build() and MyFactory.create() will return instances of MyModel
    """

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> T:  # type: ignore[misc]
        return super().__new__(*args, **kwargs)

    @classmethod
    def create(cls, **kwargs: typing.Any) -> T:
        return super().create(**kwargs)

    @classmethod
    def build(cls, **kwargs: typing.Any) -> T:
        return super().build(**kwargs)

    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
