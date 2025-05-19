from flask import flash
from flask import render_template
from markupsafe import Markup
import pydantic.v1 as pydantic_v1
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.connectors.serialization import titelive_serializers
from pcapi.connectors.titelive import get_by_ean13
import pcapi.core.fraud.models as fraud_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.offers.serializer import OfferSerializer


list_products_blueprint = utils.child_backoffice_blueprint(
    "product",
    __name__,
    url_prefix="/pro/product",
    permission=perm_models.Permissions.READ_OFFERS,
)


@list_products_blueprint.route("/<int:product_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_OFFERS)
def get_product_details(product_id: int) -> utils.BackofficeResponse:
    product = (
        db.session.query(offers_models.Product)
        .filter(offers_models.Product.id == product_id)
        .options(
            sa_orm.joinedload(offers_models.Product.offers).options(
                sa_orm.load_only(
                    offers_models.Offer.id,
                    offers_models.Offer.name,
                    offers_models.Offer.dateCreated,
                    offers_models.Offer.isActive,
                    offers_models.Offer.validation,
                ),
                sa_orm.joinedload(offers_models.Offer.stocks).options(
                    sa_orm.load_only(
                        offers_models.Stock.bookingLimitDatetime,
                        offers_models.Stock.beginningDatetime,
                        offers_models.Stock.quantity,
                        offers_models.Stock.dnBookedQuantity,
                        offers_models.Stock.isSoftDeleted,
                    )
                ),
                sa_orm.joinedload(offers_models.Offer.venue).options(
                    sa_orm.load_only(
                        offerers_models.Venue.id,
                        offerers_models.Venue.name,
                    )
                ),
            ),
            sa_orm.joinedload(offers_models.Product.productMediations),
        )
        .one_or_none()
    )

    if not product:
        raise NotFound()

    unlinked_offers = []
    if product.ean:
        unlinked_offers = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.ean == product.ean, offers_models.Offer.productId.is_(None))
            .options(
                sa_orm.load_only(
                    offers_models.Offer.id,
                    offers_models.Offer.name,
                    offers_models.Offer.dateCreated,
                    offers_models.Offer.isActive,
                    offers_models.Offer.validation,
                ),
                sa_orm.joinedload(offers_models.Offer.stocks).options(
                    sa_orm.load_only(
                        offers_models.Stock.bookingLimitDatetime,
                        offers_models.Stock.beginningDatetime,
                        offers_models.Stock.quantity,
                        offers_models.Stock.dnBookedQuantity,
                        offers_models.Stock.isSoftDeleted,
                    )
                ),
                sa_orm.joinedload(offers_models.Offer.venue).options(
                    sa_orm.load_only(
                        offerers_models.Venue.id,
                        offerers_models.Venue.name,
                    )
                ),
            )
            .order_by(offers_models.Offer.id)
            .all()
        )

    active_offers_count = sum(offer.isActive for offer in product.offers)
    approved_active_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and offer.isActive for offer in product.offers
    )
    approved_inactive_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and not offer.isActive for offer in product.offers
    )
    pending_offers_count = sum(offer.validation == OfferValidationStatus.PENDING for offer in product.offers)
    rejected_offers_count = sum(offer.validation == OfferValidationStatus.REJECTED for offer in product.offers)

    if product.ean:
        try:
            titelive_data = get_by_ean13(product.ean)
        except Exception as err:
            flash(
                Markup("Une erreur s'est produite : {message}").format(message=str(err) or err.__class__.__name__),
                "warning",
            )
            titelive_data = {}
        try:
            data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, titelive_data["oeuvre"])
        except Exception:
            ineligibility_reasons = None
        else:
            ineligibility_reasons = get_ineligibility_reasons(data.article[0], data.titre)

        product_whitelist = (
            db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == product.ean)
            .options(
                sa_orm.load_only(
                    fraud_models.ProductWhitelist.ean,
                    fraud_models.ProductWhitelist.dateCreated,
                    fraud_models.ProductWhitelist.comment,
                    fraud_models.ProductWhitelist.authorId,
                ),
                sa_orm.joinedload(fraud_models.ProductWhitelist.author).load_only(
                    users_models.User.firstName, users_models.User.lastName
                ),
            )
            .one_or_none()
        )
    else:
        titelive_data = None
        ineligibility_reasons = None
        product_whitelist = None

    return render_template(
        "products/details.html",
        product=product,
        provider_name=product.lastProvider.name if product.lastProvider else None,
        product_offers=[OfferSerializer.from_orm(offer).dict() for offer in sorted(product.offers, key=lambda o: o.id)],
        unlinked_offers=[OfferSerializer.from_orm(offer).dict() for offer in unlinked_offers],
        titelive_data=titelive_data,
        active_offers_count=active_offers_count,
        approved_active_offers_count=approved_active_offers_count,
        approved_inactive_offers_count=approved_inactive_offers_count,
        pending_offers_count=pending_offers_count,
        rejected_offers_count=rejected_offers_count,
        ineligibility_reasons=ineligibility_reasons,
        product_whitelist=product_whitelist,
    )
