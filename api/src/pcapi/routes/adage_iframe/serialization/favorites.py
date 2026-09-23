from pcapi.routes.adage_iframe.serialization.offers import CollectiveOfferTemplateResponseModel
from pcapi.routes.serialization import HttpBodyModel


class FavoritesResponseModel(HttpBodyModel):
    favoritesTemplate: list[CollectiveOfferTemplateResponseModel]
