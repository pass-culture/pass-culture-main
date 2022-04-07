from pcapi.core.testing import BaseFactory

from . import models


class ReferenceSchemeFactory(BaseFactory):
    class Meta:
        model = models.ReferenceScheme
        sqlalchemy_get_or_create = ["name", "year"]

    name = "invoice.reference"
    year = 2022

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        # We need to set the prefix ourselves, because it's not part
        # of the "key" of `sqlalchemy_get_or_create, and there are two
        # UNIQUE contraints on both `(name, year)` and `(prefix, year)`.
        if "prefix" not in kwargs:
            if kwargs["name"] == "invoice.reference":
                kwargs["prefix"] = "F"
            else:
                kwargs["prefix"] = kwargs["name"][0]
        return super()._create(model_class, *args, **kwargs)
