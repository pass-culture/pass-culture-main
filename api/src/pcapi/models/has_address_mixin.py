""" has address mixin """

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class HasAddressMixin:
    address = Column(String(200), nullable=True)

    postalCode = Column(String(6), nullable=False)

    city = Column(String(50), nullable=False)
