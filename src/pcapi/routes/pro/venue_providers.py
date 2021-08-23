from typing import Union

from flask_login import login_required

from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers import repository
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.flask_app import private_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderQuery
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderResponse
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.workers.venue_provider_job import venue_provider_job


@private_api.route("/venueProviders", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=ListVenueProviderResponse)
def list_venue_providers(query: ListVenueProviderQuery) -> ListVenueProviderResponse:
    venue_provider_list = repository.get_venue_provider_list(query.venue_id)
    for venue_provider in venue_provider_list:
        if venue_provider.isFromAllocineProvider:
            venue_provider.price = _allocine_venue_provider_price(venue_provider)
    return ListVenueProviderResponse(
        venue_providers=[VenueProviderResponse.from_orm(venue_provider) for venue_provider in venue_provider_list]
    )


@private_api.route("/venueProviders", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse)
def create_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    body.venueIdAtOfferProvider = None

    try:
        new_venue_provider = api.create_venue_provider(
            dehumanize(body.providerId),
            dehumanize(body.venueId),
            VenueProviderCreationPayload(
                isDuo=body.isDuo, price=body.price, venueIdAtOfferProvider=body.venueIdAtOfferProvider
            ),
        )
    except exceptions.VenueSiretNotRegistered as exc:
        raise ApiErrors(
            {
                "venue": [
                    f"L’importation d’offres avec {exc.provider_name} n’est pas disponible pour le SIRET {exc.siret}"
                ]
            }
        )
    except exceptions.VenueNotFound:
        raise ApiErrors({"venue": ["Lieu introuvable"]}, 404)
    except exceptions.NoSiretSpecified:
        raise ApiErrors({"venue": ["Le siret du lieu n'est pas défini, veuillez en définir un"]})
    except exceptions.ProviderWithoutApiImplementation:
        raise ApiErrors({"provider": ["Le provider choisir n'implémente pas notre api"]})
    except exceptions.NoAllocinePivot:
        raise ApiErrors({"allocine": ["Aucun AllocinePivot n'est défini pour ce lieu"]}, 404)
    except exceptions.NoPriceSpecified:
        raise ApiErrors({"price": ["Il est obligatoire de saisir un prix"]})
    except exceptions.VenueProviderException:
        raise ApiErrors({"global": ["Le provider n'a pas pu être enregistré"]})

    venue_provider_job.delay(new_venue_provider.id)

    if new_venue_provider.isFromAllocineProvider:
        new_venue_provider.price = _allocine_venue_provider_price(new_venue_provider)

    return VenueProviderResponse.from_orm(new_venue_provider)


def _allocine_venue_provider_price(venue_provider) -> Union[float, None]:
    for price_rule in venue_provider.priceRules:
        if price_rule.priceRule():
            return price_rule.price
    return None
