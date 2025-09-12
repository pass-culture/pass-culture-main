import typing
import uuid

import factory
from factory.faker import faker

import pcapi.core.offers.models as offers_models
from pcapi.core.categories import subcategories
from pcapi.core.factories import BaseFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.products import models as products_models


fake = faker.Faker(locale="fr_FR")

EVENT_PRODUCT_SUBCATEGORIES_IDS = [subcategories.SEANCE_CINE.id]
THINGS_PRODUCT_SUBCATEGORIES_IDS = [
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
]
ALL_PRODUCT_SUBCATEGORIES_IDS = EVENT_PRODUCT_SUBCATEGORIES_IDS + THINGS_PRODUCT_SUBCATEGORIES_IDS
OPENING_HOURS = [("10:00", "13:00"), ("14:00", "19:30")]


class ProductFactory(BaseFactory):
    AVAILABLE_SUBCATEGORIES = ALL_PRODUCT_SUBCATEGORIES_IDS

    class Meta:
        model = products_models.Product
        exclude = ("AVAILABLE_SUBCATEGORIES",)

    subcategoryId = subcategories.LIVRE_PAPIER.id
    name = factory.Sequence("Product {}".format)
    description = factory.Sequence("A passionate description of product {}".format)
    ean = factory.LazyAttribute(
        lambda o: (
            fake.ean13()
            if o.subcategoryId in THINGS_PRODUCT_SUBCATEGORIES_IDS or getattr(o, "set_all_fields", False)
            else None
        )
    )

    @classmethod
    def _create(
        cls,
        model_class: type[products_models.Product],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> products_models.Product:
        # Graciously provide the required idAtProviders if lastProvider is given.

        if kwargs["subcategoryId"] not in cls.AVAILABLE_SUBCATEGORIES:
            raise ValueError(f"Events products subcategory can only be one of {cls.AVAILABLE_SUBCATEGORIES}.")

        if "extraData" not in kwargs:
            subcategory_id = kwargs.get("subcategoryId")
            assert isinstance(
                subcategory_id, str
            )  # if the subcategoryId was not given in the factory, it will get the default subcategoryId
            kwargs["extraData"] = offers_factories.build_extra_data_from_subcategory(
                subcategory_id, kwargs.pop("set_all_fields", False), True
            )

        if kwargs.get("extraData") and "ean" in kwargs.get("extraData", {}):
            raise ValueError("'ean' key is no longer allowed in extraData. Use the ean column instead.")

        return super()._create(model_class, *args, **kwargs)


class ProductMediationFactory(BaseFactory):
    class Meta:
        model = products_models.ProductMediation

    product = factory.SubFactory(ProductFactory)
    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    imageType = offers_models.ImageType.RECTO


class EventProductFactory(ProductFactory):
    AVAILABLE_SUBCATEGORIES = EVENT_PRODUCT_SUBCATEGORIES_IDS
    subcategoryId = subcategories.SEANCE_CINE.id


class ThingProductFactory(ProductFactory):
    AVAILABLE_SUBCATEGORIES = THINGS_PRODUCT_SUBCATEGORIES_IDS
    subcategoryId = subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
