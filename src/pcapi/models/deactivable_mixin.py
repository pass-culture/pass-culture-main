""" deactivable mixin """
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql import expression


class DeactivableMixin(object):
    isActive = Column(Boolean, nullable=False, server_default=expression.true(), default=True)
