from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public import blueprints
from pcapi.routes.public import utils
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.image_conversion import DO_NOT_CROP
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (offers_serialization.AuthErrorResponseModel, "Authentification nécessaire"),
    "HTTP_403": (
        offers_serialization.ErrorResponseModel,
        "Vous n'avez pas les droits nécessaires pour voir cette offre collective",
    ),
    "HTTP_404": (offers_serialization.ErrorResponseModel, "L'offre collective n'existe pas"),
}


@blueprints.v2_prefixed_public_api.route("/collective/offers/", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (
                    offers_serialization.CollectiveOffersListResponseModel,
                    "L'offre collective existe",
                ),
            }
        )
    ),
)
@api_key_required
def get_collective_offers_public(
    query: offers_serialization.ListCollectiveOffersQueryModel,
) -> offers_serialization.CollectiveOffersListResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récuperation de l'offre collective avec l'identifiant offer_id.
    Cette api ignore les offre vitrines et les offres commencées sur l'interface web et non finalisées."""

    offers = educational_api_offer.list_public_collective_offers(
        offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
        venue_id=query.venue_id,
        status=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return offers_serialization.CollectiveOffersListResponseModel(
        __root__=[offers_serialization.CollectiveOffersResponseModel.from_orm(offer) for offer in offers]
    )


@blueprints.v2_prefixed_public_api.route("/collective/offers/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            BASE_CODE_DESCRIPTIONS
            | {
                "HTTP_200": (
                    offers_serialization.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective existe",
                ),
            }
        )
    ),
)
@api_key_required
def get_collective_offer_public(
    offer_id: int,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
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
    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprints.v2_prefixed_public_api.route("/collective/offers/", methods=["POST"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_201": (
                    offers_serialization.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective à été créée avec succes",
                ),
                "HTTP_400": (offers_serialization.ErrorResponseModel, "Requête malformée"),
                "HTTP_401": (
                    offers_serialization.AuthErrorResponseModel,
                    "Authentification nécessaire",
                ),
                "HTTP_403": (
                    offers_serialization.ErrorResponseModel,
                    "Non éligible pour les offres collectives",
                ),
                "HTTP_404": (
                    offers_serialization.ErrorResponseModel,
                    "L'une des resources pour la création de l'offre n'a pas été trouvée",
                ),
            }
        )
    ),
)
@api_key_required
def post_collective_offer_public(
    body: offers_serialization.PostCollectiveOfferBodyModel,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Création d'une offre collective."""
    image_as_bytes = None
    if body.image_file:
        try:
            image_as_bytes = utils.get_bytes_from_base64_string(body.image_file)
        except utils.InvalidBase64Exception:
            raise ApiErrors(errors={"imageFile": ["La valeur ne semble pas être du base 64 valide."]})
        try:
            offers_validation.check_image(
                image_as_bytes=image_as_bytes,
                accepted_types=offers_validation.ACCEPTED_THUMBNAIL_FORMATS,
                min_width=offers_validation.STANDARD_THUMBNAIL_WIDTH,
                min_height=offers_validation.STANDARD_THUMBNAIL_HEIGHT,
                max_width=offers_validation.STANDARD_THUMBNAIL_WIDTH,
                max_height=offers_validation.STANDARD_THUMBNAIL_HEIGHT,
            )
        except offers_exceptions.UnacceptedFileType:
            raise ApiErrors(
                errors={
                    "imageFile": [
                        f"Les formats acceptés sont:  {', '.join(offers_validation.ACCEPTED_THUMBNAIL_FORMATS)}"
                    ],
                },
                status_code=400,
            )
        except (offers_exceptions.ImageTooSmall, offers_exceptions.ImageTooLarge):
            raise ApiErrors(
                errors={
                    "imageFile": [
                        f"L'image doit faire exactement {offers_validation.STANDARD_THUMBNAIL_WIDTH}*{offers_validation.STANDARD_THUMBNAIL_HEIGHT} pixels"
                    ],
                },
                status_code=400,
            )

    try:
        offer = educational_api_offer.create_collective_offer_public(
            offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
            body=body,
        )
    except educational_exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors(
            errors={
                "global": ["Non éligible pour les offres collectives."],
            },
            status_code=403,
        )
    except offerers_exceptions.VenueNotFoundException:
        raise ApiErrors(
            errors={
                "venueId": ["Ce lieu n'à pas été trouvée."],
            },
            status_code=404,
        )
    except educational_exceptions.InvalidInterventionArea as exc:
        raise ApiErrors(
            errors={
                "interventionArea": [f"Les valeurs {exc.errors} ne sont pas valides."],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionUnknown:
        raise ApiErrors(
            errors={
                "educationalInstitutionId": ["Établissement scolaire non trouvé."],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionIsNotActive:
        raise ApiErrors(
            errors={"global": ["l'institution n'est pas active"]},
            status_code=403,
        )

    if image_as_bytes and body.image_credit is not None:
        educational_api_offer.attach_image(
            obj=offer, image=image_as_bytes, crop_params=DO_NOT_CROP, credit=body.image_credit
        )

    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprints.v2_prefixed_public_api.route("/collective/offers/<int:offer_id>", methods=["PATCH"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    offers_serialization.GetPublicCollectiveOfferResponseModel,
                    "L'offre collective à été édité avec succes",
                ),
                "HTTP_400": (offers_serialization.ErrorResponseModel, "Requête malformée"),
                "HTTP_401": (
                    offers_serialization.AuthErrorResponseModel,
                    "Authentification nécessaire",
                ),
                "HTTP_403": (
                    offers_serialization.ErrorResponseModel,
                    "Vous n'avez pas les droits nécessaires pour éditer cette offre collective",
                ),
                "HTTP_404": (
                    offers_serialization.ErrorResponseModel,
                    "L'une des resources pour la création de l'offre n'a pas été trouvée",
                ),
                "HTTP_422": (
                    offers_serialization.ErrorResponseModel,
                    "Cetains champs ne peuvent pas être édités selon l'état de l'offre",
                ),
            }
        )
    ),
)
@api_key_required
def patch_collective_offer_public(
    offer_id: int,
    body: offers_serialization.PatchCollectiveOfferBodyModel,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Édition d'une offre collective."""
    new_values = body.dict(exclude_unset=True)
    image_as_bytes = None
    image_file = False
    # checking data
    educational_validation.validate_offer_venue(body.offerVenue)
    non_nullable_fields = [
        "name",
        "venueId",
        "contactEmail",
        "contactPhone",
        "description",
        "domains",
        "students",
        "offerVenue",
        "interventionArea",
        "beginningDatetime",
        "totalPrice",
        "numberOfTickets",
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
        "isActive",
        "educational_institution_id",
    ]
    for field in non_nullable_fields:
        if field in new_values and new_values[field] is None:
            raise ApiErrors(
                errors={
                    field: ["Ce champ peut ne pas être présent mais ne peut pas être null."],
                },
                status_code=400,
            )
    if new_values.get("educationalPriceDetail", None):
        new_values["priceDetail"] = new_values.pop("educationalPriceDetail")

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

    if new_values.get("venueId"):
        venue = offerers_repository.find_venue_by_id(new_values["venueId"])
        if (not venue) or (venue.managingOffererId != current_api_key.offerer.id):  # type: ignore [attr-defined]
            raise ApiErrors(
                errors={
                    "venueId": ["Ce lieu n'a pas été trouvé."],
                },
                status_code=404,
            )

    if new_values.get("offerVenue"):
        if new_values["offerVenue"] == collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value:
            venue = offerers_repository.find_venue_by_id(new_values["offerVenue"]["venuId"])
            if (not venue) or (venue.managingOffererId != current_api_key.offerer.id):  # type: ignore [attr-defined]
                raise ApiErrors(
                    errors={
                        "offerVenue.venueId": ["Ce lieu n'a pas été trouvé."],
                    },
                    status_code=404,
                )

    # validate image_data
    if "imageCredit" in new_values:
        image_credit = new_values["imageCredit"]
        if image_credit is None and (offer.hasImage or new_values.get("imageFile", None)):
            ApiErrors(
                errors={
                    "imageCredit": [
                        "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
                    ],
                },
                status_code=400,
            )
        if image_credit is not None and not offer.hasImage and not new_values.get("imageFile", None):
            ApiErrors(
                errors={
                    "imageCredit": [
                        "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
                    ],
                },
                status_code=400,
            )

    if "imageFile" in new_values:
        if offer.imageCredit is None and not new_values.get("imageCredit", None):
            ApiErrors(
                errors={
                    "imageFile": [
                        "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
                    ],
                },
                status_code=400,
            )
        if body.imageFile:
            try:
                image_as_bytes = utils.get_bytes_from_base64_string(body.imageFile)
            except utils.InvalidBase64Exception:
                raise ApiErrors(errors={"imageFile": ["La valeur ne semble pas être du base 64 valide."]})
            try:
                offers_validation.check_image(
                    image_as_bytes=image_as_bytes,
                    accepted_types=offers_validation.ACCEPTED_THUMBNAIL_FORMATS,
                    min_width=offers_validation.STANDARD_THUMBNAIL_WIDTH,
                    min_height=offers_validation.STANDARD_THUMBNAIL_HEIGHT,
                    max_width=offers_validation.STANDARD_THUMBNAIL_WIDTH,
                    max_height=offers_validation.STANDARD_THUMBNAIL_HEIGHT,
                )
            except offers_exceptions.UnacceptedFileType:
                raise ApiErrors(
                    errors={
                        "imageFile": [
                            f"Les formats acceptés sont:  {', '.join(offers_validation.ACCEPTED_THUMBNAIL_FORMATS)}"
                        ],
                    },
                    status_code=400,
                )
            except (offers_exceptions.ImageTooSmall, offers_exceptions.ImageTooLarge):
                raise ApiErrors(
                    errors={
                        "imageFile": [
                            f"L'image doit faire exactement {offers_validation.STANDARD_THUMBNAIL_WIDTH}*{offers_validation.STANDARD_THUMBNAIL_HEIGHT} pixels"
                        ],
                    },
                    status_code=400,
                )
        image_file = new_values.pop("imageFile")

    # real edition
    try:
        offer = educational_api_offer.edit_collective_offer_public(
            offerer_id=current_api_key.offererId,  # type: ignore [attr-defined]
            new_values=new_values,
            offer=offer,
        )
    except educational_exceptions.EducationalInstitutionIsNotActive:
        raise ApiErrors(
            errors={
                "global": ["cet institution est expiré."],
            },
            status_code=403,
        )
    except educational_exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors(
            errors={
                "global": ["Non éligible pour les offres collectives."],
            },
            status_code=403,
        )
    except offerers_exceptions.VenueNotFoundException:
        raise ApiErrors(
            errors={
                "venueId": ["Ce lieu n'a pas été trouvé."],
            },
            status_code=404,
        )
    except educational_exceptions.InvalidInterventionArea as exc:
        raise ApiErrors(
            errors={
                "interventionArea": [f"Les valeurs {exc.errors} ne sont pas valides."],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionUnknown:
        raise ApiErrors(
            errors={
                "educationalInstitutionId": ["Établissement scolaire non trouvé."],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalDomainsNotFound:
        raise ApiErrors(
            errors={
                "domains": ["Domaine scolaire non trouvé."],
            },
            status_code=404,
        )
    except educational_exceptions.CollectiveOfferNotEditable:
        raise ApiErrors(
            errors={
                "global": ["Offre non éditable."],
            },
            status_code=422,
        )

    if image_as_bytes and offer.imageCredit is not None:
        educational_api_offer.attach_image(
            obj=offer, image=image_as_bytes, crop_params=DO_NOT_CROP, credit=offer.imageCredit
        )
    elif image_file is None:
        educational_api_offer.delete_image(obj=offer)

    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)
