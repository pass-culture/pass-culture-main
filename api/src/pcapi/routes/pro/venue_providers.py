from flask_login import current_user
from flask_login import login_required
from sqlalchemy.orm import exc as orm_exc
from werkzeug.exceptions import NotFound

import pcapi.core.offerers.models as offerers_models
from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers import repository
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.core.providers.repository import get_venue_provider_by_venue_and_provider_ids
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderQuery
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderResponse
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest
from pcapi.workers.venue_provider_job import venue_provider_job

from . import blueprint


def _get_venue_or_404(venue_id: int) -> offerers_models.Venue:
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
    if not venue:
        raise NotFound
    return venue


@private_api.route("/venueProviders", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=ListVenueProviderResponse, api=blueprint.pro_private_schema)
def list_venue_providers(query: ListVenueProviderQuery) -> ListVenueProviderResponse:
    venue = _get_venue_or_404(query.venue_id)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    venue_provider_list = repository.get_venue_provider_list(query.venue_id)
    return ListVenueProviderResponse(
        venue_providers=[VenueProviderResponse.from_orm(venue_provider) for venue_provider in venue_provider_list]
    )


@private_api.route("/venueProviders", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse, api=blueprint.pro_private_schema)
def create_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    body.venueIdAtOfferProvider = None
    venue = _get_venue_or_404(body.venueId)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

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

    return VenueProviderResponse.from_orm(new_venue_provider)


@private_api.route("/venueProviders", methods=["PUT"])
@login_required
@spectree_serialize(on_success_status=200, response_model=VenueProviderResponse, api=blueprint.pro_private_schema)
def update_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    venue = _get_venue_or_404(body.venueId)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    venue_provider = get_venue_provider_by_venue_and_provider_ids(body.venueId, body.providerId)

    if not venue_provider:
        raise NotFound

    updated = api.update_venue_provider(venue_provider, body)
    return VenueProviderResponse.from_orm(updated)


@private_api.route("/venueProviders/<int:venue_provider_id>", methods=["DELETE"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_provider(venue_provider_id: int) -> None:
    try:
        venue_provider = repository.get_venue_provider_by_id(venue_provider_id)
    except orm_exc.NoResultFound:
        raise NotFound()

    rest.check_user_has_access_to_offerer(current_user, venue_provider.venue.managingOffererId)

    api.delete_venue_provider(venue_provider, author=current_user)
