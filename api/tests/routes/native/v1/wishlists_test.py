import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.wishlists import models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def _create_wishlist(client, **payload):
    response = client.post("/native/v1/wishlists", json={"name": "10 films qui m'ont marqué", **payload})
    assert response.status_code == 200
    return response.json


class WishlistCrudTest:
    def test_create_update_list_and_delete(self, client):
        user = users_factories.UserFactory(firstName="Ouiche")
        client.with_token(user)

        wishlist = _create_wishlist(client, description="Ma s\u00e9lection")

        assert wishlist["visibility"] == "private"
        assert wishlist["isOwner"] is True
        assert wishlist["shareToken"]
        assert wishlist["owner"] == {"id": user.id, "firstName": "Ouiche"}
        assert wishlist["items"] == []

        response = client.patch(
            f"/native/v1/wishlists/{wishlist['id']}",
            json={"name": "  Mes envies de lecture pour 2010 ", "visibility": "public"},
        )
        assert response.status_code == 200
        assert response.json["name"] == "Mes envies de lecture pour 2010"
        assert response.json["visibility"] == "public"
        assert response.json["description"] == "Ma s\u00e9lection"

        listing = client.get("/native/v1/users/me/wishlists")
        assert listing.status_code == 200
        assert [w["id"] for w in listing.json["wishlists"]] == [wishlist["id"]]

        response = client.delete(f"/native/v1/wishlists/{wishlist['id']}")
        assert response.status_code == 204
        assert db.session.query(models.Wishlist).count() == 0

    @pytest.mark.parametrize("name", ["", "   ", "a" * 101])
    def test_invalid_name_returns_400(self, client, name):
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/wishlists", json={"name": name})

        assert response.status_code == 400

    def test_cannot_modify_other_user_wishlist(self, client):
        client.with_token(users_factories.UserFactory())
        wishlist = _create_wishlist(client, visibility="public")
        client.with_token(users_factories.UserFactory())

        assert client.patch(f"/native/v1/wishlists/{wishlist['id']}", json={"name": "x"}).status_code == 404
        assert client.delete(f"/native/v1/wishlists/{wishlist['id']}").status_code == 404
        artist = artist_factories.ArtistFactory()
        response = client.post(f"/native/v1/wishlists/{wishlist['id']}/items", json={"artistId": artist.id})
        assert response.status_code == 404


class WishlistVisibilityTest:
    @pytest.mark.parametrize(
        "visibility,by_id,by_token,in_search",
        [("private", 404, 404, False), ("unlisted", 404, 200, False), ("public", 200, 200, True)],
    )
    def test_access_for_other_user(self, client, visibility, by_id, by_token, in_search):
        client.with_token(users_factories.UserFactory())
        wishlist = _create_wishlist(client, visibility=visibility)
        client.with_token(users_factories.UserFactory())

        assert client.get(f"/native/v1/wishlists/{wishlist['id']}").status_code == by_id
        response = client.get(f"/native/v1/wishlists/shared/{wishlist['shareToken']}")
        assert response.status_code == by_token
        if by_token == 200:
            assert response.json["isOwner"] is False
            assert response.json["shareToken"] is None
        search = client.get("/native/v1/wishlists/search?q=FILMS")
        assert search.status_code == 200
        assert bool(search.json["wishlists"]) is in_search

    @pytest.mark.parametrize(
        "visibility,expected_status",
        [
            (models.WishlistVisibility.PRIVATE, 404),
            (models.WishlistVisibility.UNLISTED, 200),
            (models.WishlistVisibility.PUBLIC, 200),
        ],
    )
    def test_shared_link_without_authentication(self, client, visibility, expected_status):
        wishlist = models.Wishlist(user=users_factories.UserFactory(), name="Partag\u00e9e", visibility=visibility)
        db.session.add(models.WishlistItem(wishlist=wishlist, artist=artist_factories.ArtistFactory(), position=0))
        db.session.flush()

        response = client.get(f"/native/v1/wishlists/shared/{wishlist.share_token}")

        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json["isOwner"] is False
            assert response.json["shareToken"] is None
            assert len(response.json["items"]) == 1

    def test_other_routes_still_require_authentication(self, client):
        assert client.get("/native/v1/users/me/wishlists").status_code == 401
        assert client.post("/native/v1/wishlists", json={"name": "Films"}).status_code == 401
        assert client.patch("/native/v1/wishlists/1", json={"name": "Films"}).status_code == 401
        assert client.delete("/native/v1/wishlists/1").status_code == 401
        assert client.post("/native/v1/wishlists/1/items", json={"workId": 1}).status_code == 401
        assert client.delete("/native/v1/wishlists/1/items/1").status_code == 401
        assert client.put("/native/v1/wishlists/1/items/order", json={"itemIds": []}).status_code == 401

    @pytest.mark.parametrize("visibility", list(models.WishlistVisibility))
    @pytest.mark.parametrize("with_item", [False, True])
    def test_detail_without_authentication(self, client, visibility, with_item):
        wishlist = models.Wishlist(user=users_factories.UserFactory(), name="Films", visibility=visibility)
        db.session.add(wishlist)
        if with_item:
            db.session.add(models.WishlistItem(wishlist=wishlist, artist=artist_factories.ArtistFactory(), position=0))
        db.session.flush()

        response = client.get(f"/native/v1/wishlists/{wishlist.id}")

        if visibility != models.WishlistVisibility.PUBLIC:
            assert response.status_code == 404
        else:
            assert response.status_code == 200
            assert response.json["isOwner"] is False
            assert response.json["shareToken"] is None
            assert isinstance(response.json["items"], list)
            assert len(response.json["items"]) == int(with_item)

    @pytest.mark.parametrize("visibility", list(models.WishlistVisibility))
    def test_owner_can_read_own_list(self, client, visibility):
        user = users_factories.UserFactory()
        wishlist = models.Wishlist(user=user, name="Films", visibility=visibility)
        db.session.add(wishlist)
        db.session.flush()
        client.with_token(user)

        response = client.get(f"/native/v1/wishlists/{wishlist.id}")

        assert response.status_code == 200
        assert response.json["isOwner"] is True
        assert response.json["shareToken"] == wishlist.share_token

    @pytest.mark.parametrize("page,expected_count", [(1, 2), (2, 1), (3, 0)])
    def test_anonymous_search_total_before_pagination(self, client, page, expected_count):
        user = users_factories.UserFactory()
        public_lists = [
            models.Wishlist(user=user, name=f"Films {index}", visibility=models.WishlistVisibility.PUBLIC)
            for index in range(3)
        ]
        db.session.add_all(
            public_lists
            + [
                models.Wishlist(user=user, name="Films secrets", visibility=models.WishlistVisibility.PRIVATE),
                models.Wishlist(user=user, name="Films par lien", visibility=models.WishlistVisibility.UNLISTED),
                models.Wishlist(user=user, name="Livres", visibility=models.WishlistVisibility.PUBLIC),
            ]
        )
        db.session.flush()

        response = client.get(f"/native/v1/wishlists/search?q=FILMS&page={page}&limit=2")

        assert response.status_code == 200
        assert response.json["nbResults"] == 3
        assert response.json["page"] == page
        assert response.json["limit"] == 2
        results = response.json["wishlists"]
        assert len(results) == expected_count
        assert [wishlist["id"] for wishlist in results] == [wishlist.id for wishlist in reversed(public_lists)][
            (page - 1) * 2 : page * 2
        ]

    def test_anonymous_search_without_results(self, client):
        response = client.get("/native/v1/wishlists/search?q=inexistant")

        assert response.status_code == 200
        assert response.json["nbResults"] == 0
        assert response.json["wishlists"] == []

    def test_unknown_detail_without_authentication(self, client):
        assert client.get("/native/v1/wishlists/999999").status_code == 404

    def test_search_escapes_wildcards(self, client):
        client.with_token(users_factories.UserFactory())
        _create_wishlist(client, visibility="public")

        response = client.get("/native/v1/wishlists/search?q=%25%25")

        assert response.status_code == 200
        assert response.json["wishlists"] == []
        assert response.json["nbResults"] == 0

    def test_search_query_too_short(self, client):
        assert client.get("/native/v1/wishlists/search?q=a").status_code == 400


class WishlistItemsTest:
    def test_add_items_reorder_and_remove(self, client):
        client.with_token(users_factories.UserFactory())
        wishlist = _create_wishlist(client)
        artist = artist_factories.ArtistFactory()
        work = discoveries_models.Work(title="Un film", media_type=discoveries_models.WorkMediaType.FILM)
        offer = offers_factories.OfferFactory(product=offers_factories.ProductFactory(work=work))
        url = f"/native/v1/wishlists/{wishlist['id']}/items"

        assert client.post(url, json={"artistId": artist.id}).status_code == 200
        response = client.post(url, json={"offerId": offer.id})
        assert response.status_code == 200
        # Adding the same work again is idempotent.
        response = client.post(url, json={"workId": work.id})
        assert response.status_code == 200
        items = response.json["items"]
        assert [(i["position"], bool(i["artist"]), bool(i["work"])) for i in items] == [
            (0, True, False),
            (1, False, True),
        ]
        assert items[1]["work"]["title"] == "Un film"

        response = client.put(f"{url}/order", json={"itemIds": [items[1]["id"], items[0]["id"]]})
        assert response.status_code == 200
        assert [i["id"] for i in response.json["items"]] == [items[1]["id"], items[0]["id"]]

        assert client.delete(f"{url}/{items[0]['id']}").status_code == 204
        assert db.session.query(models.WishlistItem).count() == 1

    @pytest.mark.parametrize("case", ["empty", "duplicate", "unknown"])
    def test_invalid_reorder_returns_400(self, client, case):
        client.with_token(users_factories.UserFactory())
        wishlist = _create_wishlist(client)
        url = f"/native/v1/wishlists/{wishlist['id']}/items"
        item_id = client.post(url, json={"artistId": artist_factories.ArtistFactory().id}).json["items"][0]["id"]
        item_ids = {"empty": [], "duplicate": [item_id, item_id], "unknown": [item_id + 1000]}[case]

        assert client.put(f"{url}/order", json={"itemIds": item_ids}).status_code == 400

    def test_unknown_target_returns_404(self, client):
        client.with_token(users_factories.UserFactory())
        wishlist = _create_wishlist(client)

        response = client.post(f"/native/v1/wishlists/{wishlist['id']}/items", json={"workId": 999999})

        assert response.status_code == 404
