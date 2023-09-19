from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import exceptions as provider_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.public import utils as shared_utils
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.united import utils
from pcapi.utils.image_conversion import DO_NOT_CROP
from pcapi.validation.routes.users_authentifications import current_api_key


COLLECTIVE_OFFERS_TAG = "Collective offers"


@utils.public_api_route("/collective-offers", method="POST", tags=[COLLECTIVE_OFFERS_TAG])
def create_collective_offer(
    body: offers_serialization.PostCollectiveOfferBodyModel,
) -> offers_serialization.GetPublicCollectiveOfferResponseModel:
    """Create a collective offer"""
    image_as_bytes = None
    if body.image_file:
        try:
            image_as_bytes = shared_utils.get_bytes_from_base64_string(body.image_file)
        except shared_utils.InvalidBase64Exception:
            raise ApiErrors(errors={"imageFile": ["Does not seem to be a valid base64 value"]})
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
                    "imageFile": [f"Accepted formats are:  {', '.join(offers_validation.ACCEPTED_THUMBNAIL_FORMATS)}"],
                },
                status_code=400,
            )
        except (offers_exceptions.ImageTooSmall, offers_exceptions.ImageTooLarge):
            raise ApiErrors(
                errors={
                    "imageFile": [
                        (
                            f"Image must be between {offers_validation.STANDARD_THUMBNAIL_WIDTH} "
                            f"* {offers_validation.STANDARD_THUMBNAIL_HEIGHT} pixels"
                        )
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
                "global": ["Uneligible for collective offers"],
            },
            status_code=403,
        )
    # Note: can it really be raised by create_collective_offer_public ?
    except provider_exceptions.ProviderNotFound:
        raise ApiErrors(
            errors={
                "Provider": ["Unknown provider"],
            },
            status_code=404,
        )
    except offerers_exceptions.VenueNotFoundException:
        raise ApiErrors(
            errors={
                "venueId": ["Unknown venue"],
            },
            status_code=404,
        )
    # Note: can be removed (not raised anywhere)
    except educational_exceptions.InvalidInterventionArea as exc:
        raise ApiErrors(
            errors={
                "interventionArea": [f"Values {exc.errors} are not valid"],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionUnknown:
        raise ApiErrors(
            errors={
                "educationalInstitutionId": ["Unknown educational institution"],
            },
            status_code=404,
        )
    except educational_exceptions.EducationalInstitutionIsNotActive:
        raise ApiErrors(
            errors={"educationalInstitutionId": ["Inactive educational institution"]},
            status_code=403,
        )
    except educational_exceptions.EducationalDomainsNotFound:
        raise ApiErrors(
            errors={"domains": ["Unknown domain"]},
            status_code=404,
        )
    except offers_exceptions.UnknownOfferSubCategory:
        raise ApiErrors(
            errors={"subcategoryId": ["Unknown subcategory"]},
            status_code=404,
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer:
        raise ApiErrors(
            errors={"subcategoryId": ["Uneligible for collective offers"]},
            status_code=404,
        )
    except offers_validation.OfferValidationError as err:
        raise ApiErrors(errors={err.field: err.msg}, status_code=400)

    if image_as_bytes and body.image_credit is not None:
        educational_api_offer.attach_image(
            obj=offer, image=image_as_bytes, crop_params=DO_NOT_CROP, credit=body.image_credit
        )

    return offers_serialization.GetPublicCollectiveOfferResponseModel.from_orm(offer)
