""" deactivable mixin """
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import expression


@declarative_mixin
class DeactivableMixin:
    isActive: bool = Column(Boolean, nullable=False, server_default=expression.true(), default=True)
