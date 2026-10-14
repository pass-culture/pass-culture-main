from flask_login import current_user

from pcapi.core.wishlists import api
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import wishlists as serializers


@blueprint.native_route("/wishlists", methods=["POST"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[400], api=blueprint.api)
def create_wishlist(body: serializers.CreateWishlistSchema) -> serializers.WishlistResponseSchema:
    wishlist = api.create_wishlist(current_user.id, body)
    return serializers.WishlistResponseSchema.build_for(wishlist, current_user.id)


@blueprint.native_route("/wishlists/<int:wishlist_id>", methods=["PATCH"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[400, 404], api=blueprint.api)
def update_wishlist(wishlist_id: int, body: serializers.UpdateWishlistSchema) -> serializers.WishlistResponseSchema:
    wishlist = api.update_wishlist(current_user.id, wishlist_id, body)
    return serializers.WishlistResponseSchema.build_for(wishlist, current_user.id)


@blueprint.native_route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(on_success_status=204, on_error_statuses=[404], api=blueprint.api)
def delete_wishlist(wishlist_id: int) -> None:
    api.delete_wishlist(current_user.id, wishlist_id)


@blueprint.native_route("/wishlists/<int:wishlist_id>", methods=["GET"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[404], api=blueprint.api)
def get_wishlist(wishlist_id: int) -> serializers.WishlistResponseSchema:
    wishlist = api.get_visible_wishlist(current_user.id, wishlist_id)
    return serializers.WishlistResponseSchema.build_for(wishlist, current_user.id)


@blueprint.native_route("/wishlists/shared/<string:share_token>", methods=["GET"])
@atomic()
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[404], api=blueprint.api)
def get_shared_wishlist(share_token: str) -> serializers.WishlistResponseSchema:
    wishlist = api.get_wishlist_by_token(share_token)
    user_id = None if current_user.is_anonymous else current_user.id
    return serializers.WishlistResponseSchema.build_for(wishlist, user_id)


@blueprint.native_route("/wishlists/search", methods=["GET"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistsResponseSchema, on_error_statuses=[400], api=blueprint.api)
def search_wishlists(query: serializers.WishlistSearchQuerySchema) -> serializers.WishlistsResponseSchema:
    wishlists = api.search_public_wishlists(query.q, query.page, query.limit)
    return serializers.WishlistsResponseSchema(
        page=query.page,
        limit=query.limit,
        wishlists=[serializers.WishlistSummaryResponseSchema.build(wishlist) for wishlist in wishlists],
    )


@blueprint.native_route("/users/me/wishlists", methods=["GET"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistsResponseSchema, api=blueprint.api)
def get_user_wishlists(query: serializers.WishlistsQuerySchema) -> serializers.WishlistsResponseSchema:
    wishlists = api.get_user_wishlists(current_user.id, query.page, query.limit)
    return serializers.WishlistsResponseSchema(
        page=query.page,
        limit=query.limit,
        wishlists=[serializers.WishlistSummaryResponseSchema.build(wishlist) for wishlist in wishlists],
    )


@blueprint.native_route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[400, 404], api=blueprint.api)
def add_wishlist_item(wishlist_id: int, body: serializers.AddWishlistItemSchema) -> serializers.WishlistResponseSchema:
    wishlist = api.add_item(current_user.id, wishlist_id, body)
    return serializers.WishlistResponseSchema.build_for(wishlist, current_user.id)


@blueprint.native_route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(on_success_status=204, on_error_statuses=[404], api=blueprint.api)
def remove_wishlist_item(wishlist_id: int, item_id: int) -> None:
    api.remove_item(current_user.id, wishlist_id, item_id)


@blueprint.native_route("/wishlists/<int:wishlist_id>/items/order", methods=["PUT"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.WishlistResponseSchema, on_error_statuses=[400, 404], api=blueprint.api)
def reorder_wishlist_items(
    wishlist_id: int, body: serializers.ReorderWishlistItemsSchema
) -> serializers.WishlistResponseSchema:
    wishlist = api.reorder_items(current_user.id, wishlist_id, body.item_ids)
    return serializers.WishlistResponseSchema.build_for(wishlist, current_user.id)
