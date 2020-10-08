""" has address mixin """

from sqlalchemy import Column, String


class HasAddressMixin(object):
    address = Column(String(200), nullable=True)

    postalCode = Column(String(6), nullable=False)

    city = Column(String(50), nullable=False)
