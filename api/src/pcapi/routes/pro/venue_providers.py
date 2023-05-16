from flask_login import current_user
from flask_login import login_required

from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers import repository
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.core.providers.repository import get_venue_provider_by_venue_and_provider_ids
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderQuery
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderResponse
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authorizations import check_user_can_alter_venue
from pcapi.workers.venue_provider_job import venue_provider_job

from . import blueprint


@private_api.route("/venueProviders", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=ListVenueProviderResponse, api=blueprint.pro_private_schema)  # type: ignore [arg-type]
def list_venue_providers(query: ListVenueProviderQuery) -> ListVenueProviderResponse:
    check_user_can_alter_venue(current_user, query.venue_id)

    venue_provider_list = repository.get_venue_provider_list(query.venue_id)
    for venue_provider in venue_provider_list:
        if venue_provider.isFromAllocineProvider:
            venue_provider.price = _allocine_venue_provider_price(venue_provider)
    return ListVenueProviderResponse(
        venue_providers=[VenueProviderResponse.from_orm(venue_provider) for venue_provider in venue_provider_list]
    )


@private_api.route("/venueProviders", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse, api=blueprint.pro_private_schema)  # type: ignore [arg-type]
def create_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    body.venueIdAtOfferProvider = None
    if body.venueId is None:
        raise ApiErrors({"venue": ["Lieu introuvable."]}, 404)
    check_user_can_alter_venue(current_user, body.venueId)

    try:
        new_venue_provider = api.create_venue_provider(
            body.providerId,
            body.venueId,
            VenueProviderCreationPayload(
                isDuo=body.isDuo,
                price=body.price,
                quantity=body.quantity,
                venueIdAtOfferProvider=body.venueIdAtOfferProvider,
            ),
        )
    except exceptions.VenueSiretNotRegistered as exc:
        raise ApiErrors(
            {
                "venue": [
                    f"L’importation d’offres avec {exc.provider_name} n’est pas disponible pour le SIRET {exc.siret}."
                ]
            }
        )
    except exceptions.VenueNotFound:
        raise ApiErrors({"venue": ["Lieu introuvable."]}, 404)
    except exceptions.NoSiretSpecified:
        raise ApiErrors({"venue": ["Le siret du lieu n'est pas défini, veuillez en définir un."]})
    except exceptions.ProviderWithoutApiImplementation:
        raise ApiErrors(
            {"provider": ["Le fournisseur choisi n'est pas correctement implémenté, veuillez contacter le support."]}
        )
    except exceptions.UnknownVenueToAlloCine:
        raise ApiErrors(
            {
                "allocine": [
                    "Ce lieu n'est pas autorisé à être synchronisé avec Allociné. Veuillez contacter le support si vous souhaitez le faire."
                ]
            },
            404,
        )
    except exceptions.NoCinemaProviderPivot:
        raise ApiErrors(
            {
                "cinema_provider": [
                    "Ce lieu n'est pas configuré pour effectuer une synchronisation avec nos fournisseurs."
                ]
            },
            404,
        )
    except exceptions.NoPriceSpecified:
        raise ApiErrors({"price": ["Il est obligatoire de saisir un prix."]})
    except exceptions.VenueProviderException:
        raise ApiErrors({"global": ["Le fournisseur n'a pas pu être configuré."]})

    # We don't want to start a synchronization for providers linked to an offerer
    # since creating a venue_provider in this case only delegate the right for an
    # offerer to create offers for this venue. (we don't synchronize anything ourselves)
    if not new_venue_provider.provider.hasOffererProvider:
        venue_provider_job.delay(new_venue_provider.id)

    if new_venue_provider.isFromAllocineProvider:
        new_venue_provider.price = _allocine_venue_provider_price(new_venue_provider)

    return VenueProviderResponse.from_orm(new_venue_provider)


@private_api.route("/venueProviders", methods=["PUT"])
@login_required
@spectree_serialize(on_success_status=200, response_model=VenueProviderResponse, api=blueprint.pro_private_schema)  # type: ignore [arg-type]
def update_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    assert body.venueId is not None, "a not None venue_id is required"
    assert body.providerId is not None, "a not None provider_id is required"

    check_user_can_alter_venue(current_user, body.venueId)

    venue_provider = get_venue_provider_by_venue_and_provider_ids(body.venueId, body.providerId)

    updated = api.update_venue_provider(venue_provider, body)
    if updated.isFromAllocineProvider:
        updated.price = _allocine_venue_provider_price(updated)

    return VenueProviderResponse.from_orm(updated)


@private_api.route("/venueProviders/<int:venue_provider_id>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_provider(venue_provider_id: int) -> None:
    assert venue_provider_id is not None, "a not None provider_id is required"

    venue_provider = repository.get_venue_provider_by_id(int(venue_provider_id))

    check_user_can_alter_venue(current_user, venue_provider.venueId)

    api.delete_venue_provider(venue_provider)


def _allocine_venue_provider_price(venue_provider: AllocineVenueProvider) -> float | None:
    for price_rule in venue_provider.priceRules:
        if price_rule.priceRule():
            return price_rule.price
    return None
