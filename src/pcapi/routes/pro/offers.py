import base64
import logging

from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.offers import exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.validation import check_image
from pcapi.core.offers.validation import get_distant_image
from pcapi.models import ApiErrors
from pcapi.models import Offer
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailBodyModel
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.workers.update_all_offers_active_status_job import update_all_offers_active_status_job


logger = logging.getLogger(__name__)
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404


@private_api.route("/offers", methods=["GET"])
@login_required
@spectree_serialize(response_model=offers_serialize.ListOffersResponseModel)  # type: ignore
def list_offers(query: offers_serialize.ListOffersQueryModel) -> offers_serialize.ListOffersResponseModel:
    paginated_offers = offers_api.list_offers_for_pro_user(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        category_id=query.categoryId,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        name_keywords_or_isbn=query.nameOrIsbn,
        status=query.status,
        creation_mode=query.creation_mode,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return offers_serialize.ListOffersResponseModel(__root__=serialize_offers_recap_paginated(paginated_offers))


@private_api.route("/offers/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=offers_serialize.GetOfferResponseModel)
def get_offer(offer_id: str) -> offers_serialize.GetOfferResponseModel:
    offer = load_or_404(Offer, offer_id)
    return offers_serialize.GetOfferResponseModel.from_orm(offer)


@private_api.route("/offers", methods=["POST"])
@login_required
@spectree_serialize(response_model=offers_serialize.OfferResponseIdModel, on_success_status=201)  # type: ignore
def post_offer(body: offers_serialize.PostOfferBodyModel) -> offers_serialize.OfferResponseIdModel:
    try:
        offer = offers_api.create_offer(offer_data=body, user=current_user)

    except exceptions.OfferCannotBeDuoAndEducational as error:
        logger.info(
            "Could not create offer: offer cannot be both 'duo' and 'educational'",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )

    except exceptions.UnknownOfferSubCategory as error:
        logger.info(
            "Could not create offer: selected subcategory is unknown.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )

    except exceptions.SubCategoryIsInactive as error:
        logger.info(
            "Could not create offer: subcategory cannot be selected.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )

    except exceptions.SubcategoryNotEligibleForEducationalOffer as error:
        logger.info(
            "Could not create offer: subcategory is not eligible for educational offer.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )

    return offers_serialize.OfferResponseIdModel.from_orm(offer)


@private_api.route("/offers/active-status", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204)  # type: ignore
def patch_offers_active_status(body: offers_serialize.PatchOfferActiveStatusBodyModel) -> None:
    query = offers_repository.get_offers_by_ids(current_user, body.ids)
    offers_api.batch_update_offers(query, {"isActive": body.is_active})


@private_api.route("/offers/all-active-status", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=202)
def patch_all_offers_active_status(
    body: offers_serialize.PatchAllOffersActiveStatusBodyModel,
) -> offers_serialize.PatchAllOffersActiveStatusResponseModel:
    filters = {
        "user_id": current_user.id,
        "is_user_admin": current_user.isAdmin,
        "offerer_id": body.offerer_id,
        "status": body.status,
        "venue_id": body.venue_id,
        "category_id": body.category_id,
        "name_or_isbn": body.name_or_isbn,
        "creation_mode": body.creation_mode,
        "period_beginning_date": body.period_beginning_date,
        "period_ending_date": body.period_ending_date,
    }
    update_all_offers_active_status_job.delay(filters, body.is_active)
    return offers_serialize.PatchAllOffersActiveStatusResponseModel()


@private_api.route("/offers/<offer_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=offers_serialize.OfferResponseIdModel)  # type: ignore
def patch_offer(offer_id: str, body: offers_serialize.PatchOfferBodyModel) -> offers_serialize.OfferResponseIdModel:
    offer = load_or_404(Offer, human_id=offer_id)
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    offer = offers_api.update_offer(offer, **body.dict(exclude_unset=True))

    return offers_serialize.OfferResponseIdModel.from_orm(offer)


@private_api.route("/offers/thumbnail-url-validation", methods=["POST"])
@login_required
@spectree_serialize(response_model=offers_serialize.ImageResponseModel)
def validate_distant_image(body: offers_serialize.ImageBodyModel) -> offers_serialize.ImageResponseModel:
    errors = []

    try:
        image = get_distant_image(body.url)
        check_image(image)
        image_as_base64 = base64.b64encode(image)
        return offers_serialize.ImageResponseModel(
            image=f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}', errors=errors
        )
    except (
        exceptions.FileSizeExceeded,
        exceptions.ImageTooSmall,
        exceptions.UnacceptedFileType,
        exceptions.FailureToRetrieve,
    ) as exc:
        logger.info("When validating image at: %s, this error was encountered: %s", body.url, exc.__class__.__name__)
        errors.append(exc.args[0])

    return offers_serialize.ImageResponseModel(errors=errors)


@private_api.route("/offers/thumbnails/", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=CreateThumbnailResponseModel)
def create_thumbnail(form: CreateThumbnailBodyModel) -> CreateThumbnailResponseModel:
    check_user_has_access_to_offerer(current_user, form.offerer_id)
    offer = get_offer_by_id(form.offer_id)

    image_as_bytes = form.get_image_as_bytes(request)
    thumbnail = offers_api.create_mediation(
        user=current_user,
        offer=offer,
        credit=form.credit,
        image_as_bytes=image_as_bytes,
        crop_params=form.crop_params,
    )

    return CreateThumbnailResponseModel(id=thumbnail.id)


@private_api.route("/offers/categories", methods=["GET"])
@login_required
@spectree_serialize(response_model=offers_serialize.CategoriesResponseModel)
def get_categories() -> offers_serialize.CategoriesResponseModel:
    return offers_serialize.CategoriesResponseModel(
        categories=[
            offers_serialize.CategoryResponseModel.from_orm(category) for category in categories.ALL_CATEGORIES
        ],
        subcategories=[
            offers_serialize.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
    )
