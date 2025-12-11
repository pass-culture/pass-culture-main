import decimal
import functools

from flask_login import current_user
from flask_login import login_required
from sqlalchemy.orm import exc as orm_exc
from werkzeug.exceptions import NotFound

import pcapi.core.offerers.models as offerers_models
from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import venue_provider_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit
from pcapi.workers.venue_provider_job import venue_provider_job

from . import blueprint


def _get_venue_or_404(venue_id: int) -> offerers_models.Venue:
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
    if not venue:
        raise NotFound
    return venue


def _get_provider_or_404(provider_id: int) -> providers_models.Provider:
    provider = db.session.query(providers_models.Provider).filter_by(id=provider_id).one_or_none()
    if not provider:
        raise NotFound
    return provider


@private_api.route("/venueProviders", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=venue_provider_serialize.ListVenueProviderResponse,
    api=blueprint.pro_private_schema,
)
def list_venue_providers(
    query: venue_provider_serialize.ListVenueProviderQuery,
) -> venue_provider_serialize.ListVenueProviderResponse:
    venue = _get_venue_or_404(query.venue_id)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    venue_provider_list = providers_repository.get_venue_provider_list(query.venue_id)
    return venue_provider_serialize.ListVenueProviderResponse(
        venue_providers=[
            venue_provider_serialize.VenueProviderResponse.model_validate(venue_provider)
            for venue_provider in venue_provider_list
        ]
    )


@private_api.route("/venueProviders/<int:venue_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=venue_provider_serialize.ListProviderResponse,
    on_success_status=200,
    on_error_statuses=[401, 404],
    api=blueprint.pro_private_schema,
)
def get_providers_by_venue(venue_id: int) -> venue_provider_serialize.ListProviderResponse:
    venue = get_or_404(offerers_models.Venue, venue_id)
    providers = providers_repository.get_available_providers(venue)
    return venue_provider_serialize.ListProviderResponse(
        [venue_provider_serialize.ProviderResponse.model_validate(provider) for provider in providers]
    )


@private_api.route("/venueProviders", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=venue_provider_serialize.VenueProviderResponse,
    api=blueprint.pro_private_schema,
)
def create_venue_provider(
    body: venue_provider_serialize.PostVenueProviderBody,
) -> venue_provider_serialize.VenueProviderResponse:
    body.venue_id_at_offer_provider = None
    venue = _get_venue_or_404(body.venue_id)
    provider = _get_provider_or_404(body.provider_id)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    try:
        new_venue_provider = api.create_venue_provider(
            provider=provider,
            venue=venue,
            current_user=current_user,
            payload=VenueProviderCreationPayload(
                isDuo=body.is_duo,
                price=decimal.Decimal(body.price) if body.price else None,
                quantity=body.quantity,
                venueIdAtOfferProvider=body.venue_id_at_offer_provider,
            ),
        )
    except exceptions.NoMatchingAllocineTheater:
        raise ResourceNotFoundError(
            {
                "allocine": [
                    "Ce lieu n'est pas autorisé à être synchronisé avec Allociné. Veuillez contacter le support si vous souhaitez le faire."
                ]
            }
        )
    except exceptions.NoCinemaProviderPivot:
        raise ResourceNotFoundError(
            {
                "cinema_provider": [
                    "Ce lieu n'est pas configuré pour effectuer une synchronisation avec nos fournisseurs."
                ]
            },
        )
    except exceptions.NoPriceSpecified:
        raise ApiErrors({"price": ["Il est obligatoire de saisir un prix."]})

    # venue_provider_job only handles movie providers now.
    movie_provider_names = {"AllocineStocks"} | set(CINEMA_PROVIDER_NAMES)
    if new_venue_provider.provider.localClass in movie_provider_names:
        on_commit(functools.partial(venue_provider_job.delay, new_venue_provider.id))

    return venue_provider_serialize.VenueProviderResponse.model_validate(new_venue_provider)


@private_api.route("/venueProviders", methods=["PUT"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=venue_provider_serialize.VenueProviderResponse,
    api=blueprint.pro_private_schema,
)
def update_venue_provider(
    body: venue_provider_serialize.PostVenueProviderBody,
) -> venue_provider_serialize.VenueProviderResponse:
    venue = _get_venue_or_404(body.venue_id)
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)

    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(body.venue_id, body.provider_id)

    if not venue_provider:
        raise NotFound

    updated = api.update_venue_provider(venue_provider, body, current_user)
    return venue_provider_serialize.VenueProviderResponse.model_validate(updated)


@private_api.route("/venueProviders/<int:venue_provider_id>", methods=["DELETE"])
@atomic()
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def delete_venue_provider(venue_provider_id: int) -> None:
    try:
        venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
    except orm_exc.NoResultFound:
        raise NotFound()

    rest.check_user_has_access_to_offerer(current_user, venue_provider.venue.managingOffererId)

    api.delete_venue_provider(venue_provider, author=current_user)
