from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.api import national_program as np_api
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.models import OfferAddressType
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public import utils
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.image_conversion import DO_NOT_CROP
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/offers/", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFERS],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (offers_serialization.CollectiveOffersListResponseModel, http_responses.HTTP_200_MESSAGE),
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def get_collective_offers_public(
    query: offers_serialization.ListCollectiveOffersQueryModel,
) -> offers_serialization.CollectiveOffersListResponseModel:
    """
    Get Collective Offers

    Return collective offers. It will only return collective offers created by API
    (collective offers created manually in the pro interface will not show up).
    """

    offers = educational_api_offer.list_public_collective_offers(
        required_id=current_api_key.providerId,
        venue_id=query.venue_id,
        status=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return offers_serialization.CollectiveOffersListResponseModel(
        __root__=[offers_serialization.CollectiveOffersResponseModel.from_orm(offer) for offer in offers]
    )


@blueprints.public_api.route("/v2/collective/offers/<int:offer_id>", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFERS],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (offers_serialization.GetPublicCollectiveOfferResponseModel, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_403_COLLECTIVE_OFFER_INSUFFICIENT_RIGHTS
            | http_responses.HTTP_404_COLLECTIVE_OFFER_NOT_FOUND
        )
    ),
)
def get_collective_offer_public(
    offer_id: int,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    """
    Get Collective Offer

    Return one collective offer using provided id.
    """
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

    if offer.providerId != current_api_key.providerId:
        msg = "Vous n'avez pas le droit d'accéder à une ressource que vous n'avez pas créée via cette API"
        raise ApiErrors(errors={"global": [msg]}, status_code=403)

    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprints.public_api.route("/v2/collective/offers/", methods=["POST"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFERS],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_201": (
                    offers_serialization.GetPublicCollectiveOfferResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                )
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_403_COLLECTIVE_OFFER_INACTIVE_INSTITUTION
            | http_responses.HTTP_404_SOME_RESOURCE_NOT_FOUND
        )
    ),
)
def post_collective_offer_public(
    body: offers_serialization.PostCollectiveOfferBodyModel,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    """
    Create Collective Offer
    """
    image_as_bytes = None

    if body.image_file:
        try:
            image_as_bytes = utils.get_bytes_from_base64_string(body.image_file)
        except utils.InvalidBase64Exception:
            raise ApiErrors(errors={"imageFile": ["La valeur ne semble pas être du base 64 valide."]})
        try:
            offers_validation.check_image(
                image_as_bytes,
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
            requested_id=current_api_key.providerId,
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
                "venueId": ["Ce lieu n'à pas été trouvé."],
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
            errors={"educationalInstitutionId": ["L'établissement scolaire n'est pas actif."]},
            status_code=403,
        )

    # domains / national_program errors
    except educational_exceptions.EducationalDomainsNotFound:
        raise ApiErrors(errors={"domains": ["Domaine scolaire non trouvé."]}, status_code=404)
    except educational_exceptions.NationalProgramNotFound:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national non trouvé."]}, status_code=404)
    except educational_exceptions.IllegalNationalProgram:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national non valide."]}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national inactif."]}, status_code=400)

    except offers_exceptions.UnknownOfferSubCategory:
        raise ApiErrors(
            errors={"subcategoryId": ["Sous-catégorie non trouvée."]},
            status_code=404,
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer:
        raise ApiErrors(
            errors={"subcategoryId": ["La sous-catégorie n'est pas éligible pour les offres collectives."]},
            status_code=404,
        )
    except educational_exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors(
            errors={"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}, status_code=400
        )
    except educational_exceptions.StartEducationalYearMissing:
        raise ApiErrors(errors={"startDatetime": ["Année scolaire manquante pour la date de début."]}, status_code=400)
    except educational_exceptions.EndEducationalYearMissing:
        raise ApiErrors(errors={"endDatetime": ["Année scolaire manquante pour la date de fin."]}, status_code=400)
    except offers_validation.OfferValidationError as err:
        raise ApiErrors(errors={err.field: err.msg}, status_code=400)

    offer_id = offer.id  # store id here to avoid re-querying it after commit from attach_image
    if image_as_bytes and body.image_credit is not None:
        educational_api_offer.attach_image(
            obj=offer, image=image_as_bytes, crop_params=DO_NOT_CROP, credit=body.image_credit
        )

    offer = educational_repository.get_collective_offer_by_id(offer_id)
    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprints.public_api.route("/v2/collective/offers/<int:offer_id>", methods=["PATCH"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFERS],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    offers_serialization.GetPublicCollectiveOfferResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                ),
            }
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_403_COLLECTIVE_OFFER_INSUFFICIENT_RIGHTS
            | http_responses.HTTP_404_SOME_RESOURCE_NOT_FOUND
        )
    ),
)
def patch_collective_offer_public(
    offer_id: int,
    body: offers_serialization.PatchCollectiveOfferBodyModel,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    """
    Update Collective Offer
    """
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
        "startDatetime",
        "endDatetime",
        "totalPrice",
        "numberOfTickets",
        "audioDisabilityCompliant",
        "mentalDisabilityCompliant",
        "motorDisabilityCompliant",
        "visualDisabilityCompliant",
        "isActive",
        "educational_institution_id",
        "formats",
    ]
    for field in non_nullable_fields:
        if field in new_values and new_values[field] is None:
            raise ApiErrors(
                errors={
                    field: ["Ce champ peut ne pas être présent mais ne peut pas être null."],
                },
                status_code=400,
            )

    if "educationalPriceDetail" in new_values:
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

    if not offer.provider or offer.provider.id != current_api_key.provider.id:
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette offre collective."],
            },
            status_code=403,
        )

    if new_values.get("venueId"):
        venue = offerers_repository.find_venue_and_provider_by_id(new_values["venueId"])
        if not venue:
            raise ApiErrors(
                errors={
                    "venueId": ["Ce lieu n'a pas été trouvé."],
                },
                status_code=404,
            )
        list_venueproviders = [
            venue_provider
            for venue_provider in venue.venueProviders
            if venue_provider.providerId == current_api_key.provider.id
        ]
        if not list_venueproviders:
            raise ApiErrors(
                errors={
                    "venueId": ["aucun lieu de fournisseur n'a été trouvé."],
                },
                status_code=403,
            )

    if new_values.get("offerVenue"):
        if new_values["offerVenue"] == OfferAddressType.OFFERER_VENUE.value:
            venue = offerers_repository.find_venue_by_id(new_values["offerVenue"]["venuId"])
            if (not venue) or (venue.managingOffererId != current_api_key.offerer.id):
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
            raise ApiErrors(
                errors={
                    "imageCredit": [
                        "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
                    ],
                },
                status_code=400,
            )
        if image_credit is not None and not offer.hasImage and not new_values.get("imageFile", None):
            raise ApiErrors(
                errors={
                    "imageCredit": [
                        "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
                    ],
                },
                status_code=400,
            )

    if "imageFile" in new_values:
        if offer.imageCredit is None and not new_values.get("imageCredit", None):
            raise ApiErrors(
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
                    image_as_bytes,
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

    national_program_id: int | None = new_values.get("nationalProgramId")
    if national_program_id is not None and np_api.get_national_program(national_program_id) is None:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif inconnu"]}, status_code=400)

    # real edition
    try:
        offer = educational_api_offer.edit_collective_offer_public(
            provider_id=current_api_key.providerId,
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

    # domains / national_program errors
    except educational_exceptions.EducationalDomainsNotFound:
        raise ApiErrors(errors={"domains": ["Domaine scolaire non trouvé."]}, status_code=404)
    except educational_exceptions.NationalProgramNotFound:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national non trouvé."]}, status_code=404)
    except educational_exceptions.IllegalNationalProgram:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national non valide."]}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        raise ApiErrors(errors={"nationalProgramId": ["Dispositif national inactif."]}, status_code=400)

    except (
        educational_exceptions.CollectiveOfferNotEditable,
        educational_exceptions.CollectiveOfferStockBookedAndBookingNotPending,
    ):
        raise ApiErrors(errors={"global": ["Offre non éditable."]}, status_code=422)
    except educational_exceptions.CollectiveOfferForbiddenFields as e:
        raise ApiErrors(
            errors={"global": [f"Seuls les champs {', '.join(e.allowed_fields)} peuvent être modifiés."]},
            status_code=400,
        )
    except educational_exceptions.PriceRequesteCantBedHigherThanActualPrice:
        raise ApiErrors(errors={"price": ["Le prix ne peut pas etre supérieur au prix existant"]}, status_code=400)
    except offers_exceptions.UnknownOfferSubCategory:
        raise ApiErrors(
            errors={"subcategoryId": ["Sous-catégorie non trouvée."]},
            status_code=404,
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer:
        raise ApiErrors(
            errors={"subcategoryId": ["La sous-catégorie n'est pas éligible pour les offres collectives."]},
            status_code=404,
        )
    except educational_exceptions.StartAndEndEducationalYearDifferent:
        raise ApiErrors(
            errors={"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}, status_code=400
        )
    except educational_exceptions.StartEducationalYearMissing:
        raise ApiErrors(errors={"startDatetime": ["Année scolaire manquante pour la date de début."]}, status_code=400)
    except educational_exceptions.EndEducationalYearMissing:
        raise ApiErrors(errors={"endDatetime": ["Année scolaire manquante pour la date de fin."]}, status_code=400)
    except offers_exceptions.BookingLimitDatetimeTooLate:
        raise ApiErrors(
            errors={
                "global": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
            },
            status_code=400,
        )
    except educational_exceptions.EndDatetimeBeforeStartDatetime:
        raise ApiErrors(
            errors={"global": ["La date de fin de l'évènement ne peut précéder la date de début."]},
            status_code=400,
        )
    except offers_validation.OfferValidationError as err:
        raise ApiErrors(errors={err.field: err.msg}, status_code=400)

    if image_as_bytes and offer.imageCredit is not None:
        educational_api_offer.attach_image(
            obj=offer, image=image_as_bytes, crop_params=DO_NOT_CROP, credit=offer.imageCredit
        )
    elif image_file is None:
        educational_api_offer.delete_image(obj=offer)

    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)


@blueprints.public_api.route("/v2/collective/offers/formats", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(**(http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS)),
)
def get_offers_formats() -> offers_serialization.GetCollectiveFormatListModel:
    """
    Get Collective Offer Formats
    """
    return offers_serialization.GetCollectiveFormatListModel(
        __root__=[
            offers_serialization.GetCollectiveFormatModel(id=format.name, name=format.value)
            for format in subcategories.EacFormat
        ]
    )
