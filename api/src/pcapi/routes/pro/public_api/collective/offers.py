from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentification nécessaire"),
    "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour voir cette offre collective"),
    "HTTP_404": (None, "L'offre collective n'existe pas"),
}


@blueprint.pro_public_api_v2.route("/collective/offers/", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListResponseModel,
                    "L'offre collective existe",
                ),
            }
        )
    ),
)
def get_collective_offers_public(
    query: public_api_collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> public_api_collective_offers_serialize.CollectiveOffersListResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récuperation de l'offre collective avec l'identifiant offer_id.
    Cette api ignore les offre vitrines et les offres commencées sur l'interface web et non finalisées."""

    offers = educational_api.list_public_collective_offers(
        offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
        venue_id=query.venue_id,
        status=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return public_api_collective_offers_serialize.CollectiveOffersListResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersResponseModel.from_orm(offer) for offer in offers
        ]
    )


@blueprint.pro_public_api_v2.route("/collective/offers/<int:offer_id>", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (
                    public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective existe",
                ),
            }
        )
    ),
)
def get_collective_offer_public(
    offer_id: int,
) -> public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récuperation de l'offre collective avec l'identifiant offer_id."""
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            errors={
                "global": ["L'offre collective n'existe pas"],
            },
            status_code=404,
        )

    if not offer.collectiveStock:
        # if the offer does not have any stock pretend it doesn't exists
        raise ApiErrors(
            errors={
                "global": ["L'offre collective n'existe pas"],
            },
            status_code=404,
        )
    if offer.venue.managingOffererId != current_api_key.offerer.id:  # type: ignore [attr-defined]
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."],
            },
            status_code=403,
        )
    return public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprint.pro_public_api_v2.route("/collective/offers/", methods=["POST"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_201": (
                    public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective à été créée avec succes",
                ),
                "HTTP_400": (None, "Requête malformée"),
                "HTTP_401": (None, "Authentification nécessaire"),
                "HTTP_403": (None, "Non éligible pour les offres collectives"),
                "HTTP_404": (None, "L'une des resources pour la création de l'offre n'a pas été trouvée"),
            }
        )
    ),
)
def post_collective_offer_public(
    body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Création d'une offre collective."""

    try:
        offer = educational_api.create_collective_offer_public(
            offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
            body=body,
        )
    except educational_exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors(
            errors={
                "global": "Non éligible pour les offres collectives.",
            },
            status_code=403,
        )
    except offerers_exceptions.VenueNotFoundException:
        raise ApiErrors(
            errors={
                "venueId": "Ce lieu n'à pas été trouvée.",
            },
            status_code=404,
        )
    except educational_exceptions.InvalidInterventionArea as exc:
        raise ApiErrors(
            errors={
                "interventionArea": f"Les valeurs {exc.errors} ne sont pas valides.",
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionUnknown:
        raise ApiErrors(
            errors={
                "educationalInstitutionId": "Établissement scolaire non trouvé.",
            },
            status_code=404,
        )

    return public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprint.pro_public_api_v2.route("/collective/offers/<int:offer_id>", methods=["PATCH"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective à été édité avec succes",
                ),
                "HTTP_400": (None, "Requête malformée"),
                "HTTP_401": (None, "Authentification nécessaire"),
                "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour éditer cette offre collective"),
                "HTTP_404": (None, "L'une des resources pour la création de l'offre n'a pas été trouvée"),
                "HTTP_422": (None, "Cetains champs ne peuvent pas être édités selon l'état de l'offre"),
            }
        )
    ),
)
def patch_collective_offer_public(
    offer_id: int,
    body: public_api_collective_offers_serialize.PatchCollectiveOfferBodyModel,
) -> public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Édition d'une offre collective."""
    new_values = body.dict(exclude_unset=True)
    # checking data
    non_nullable_fields = [
        "name",
        "contactEmail",
        "contactPhone",
        "domains",
        "students",
        "offerVenue",
        "interventionArea",
        "beginningDatetime",
        "totalPrice",
        "numberOfTickets",
    ]
    for field in non_nullable_fields:
        if field in new_values and new_values[field] is None:
            raise ApiErrors(
                errors={
                    field: "Ce champ peut ne pas être présent mais ne peut pas être null.",
                },
                status_code=400,
            )

    # access control
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            errors={
                "global": ["L'offre collective n'existe pas"],
            },
            status_code=404,
        )

    if not offer.collectiveStock:
        # if the offer does not have any stock pretend it doesn't exists
        raise ApiErrors(
            errors={
                "global": ["L'offre collective n'existe pas"],
            },
            status_code=404,
        )
    if offer.venue.managingOffererId != current_api_key.offerer.id:  # type: ignore [attr-defined]
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette offre collective."],
            },
            status_code=403,
        )

    # real edition
    try:
        offer = educational_api.edit_collective_offer_public(
            offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
            new_values=new_values,
            offer=offer,
        )
    except educational_exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors(
            errors={
                "global": "Non éligible pour les offres collectives.",
            },
            status_code=403,
        )
    except offerers_exceptions.VenueNotFoundException:
        raise ApiErrors(
            errors={
                "venueId": "Ce lieu n'a pas été trouvé.",
            },
            status_code=404,
        )
    except educational_exceptions.InvalidInterventionArea as exc:
        raise ApiErrors(
            errors={
                "interventionArea": f"Les valeurs {exc.errors} ne sont pas valides.",
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionUnknown:
        raise ApiErrors(
            errors={
                "educationalInstitutionId": "Établissement scolaire non trouvé.",
            },
            status_code=404,
        )
    except educational_exceptions.EducationalDomainsNotFound:
        raise ApiErrors(
            errors={
                "domains": "Domaine scolaire non trouvé.",
            },
            status_code=404,
        )

    return public_api_collective_offers_serialize.GetPublicCollectiveOfferResponseModel.from_orm(offer)
