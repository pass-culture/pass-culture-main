from pcapi.core.testing import BaseFactory

from . import models


class ReferenceSchemeFactory(BaseFactory):
    class Meta:
        model = models.ReferenceScheme

    name = "invoice.reference"
    prefix = "F"
    year = 2022
