from datetime import date

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.discoveries import models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class CreateDiscoveryTest:
    def test_work_is_idempotent(self, client):
        user = users_factories.UserFactory()
        work = models.Work(title="A book", media_type=models.WorkMediaType.BOOK)
        db.session.add(work)
        db.session.flush()
        client.with_token(user)
        payload = {"workId": work.id, "discoveryDate": "2026-10-12", "formatContext": "read", "sentiment": "liked"}

        response = client.post("/native/v1/discoveries", json=payload)
        duplicate = client.post("/native/v1/discoveries", json={"workId": work.id, "sentiment": "changed"})

        assert response.status_code == 200
        assert duplicate.status_code == 200
        assert response.json == duplicate.json
        assert response.json["work"]["title"] == "A book"
        assert response.json["discoveryDate"] == "2026-10-12"
        assert response.json["artist"] is None
        assert db.session.query(models.Discovery).count() == 1

    def test_artist_is_idempotent(self, client):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory(main_role="author")
        client.with_token(user)

        response = client.post("/native/v1/discoveries", json={"artistId": artist.id})
        duplicate = client.post("/native/v1/discoveries", json={"artistId": artist.id})

        assert response.status_code == 200
        assert duplicate.json == response.json
        assert response.json["artist"]["name"] == artist.name
        assert response.json["work"] is None
        assert db.session.query(models.Discovery).count() == 1

    def test_offer_resolves_work_and_main_artist(self, client):
        work = models.Work(title="A film", media_type=models.WorkMediaType.FILM)
        product = offers_factories.ProductFactory(work=work)
        offer = offers_factories.OfferFactory(product=product)
        director = artist_factories.ArtistFactory(main_role="film_director")
        db.session.add(models.WorkArtist(work=work, artist=director, role="film_director"))
        db.session.flush()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"offerId": offer.id})

        assert response.status_code == 200
        assert response.json["workId"] == work.id
        assert response.json["artistId"] is None
        assert response.json["offerOriginId"] == offer.id
        assert response.json["work"]["mainArtist"]["id"] == director.id

        duplicate = client.post("/native/v1/discoveries", json={"workId": work.id})
        assert duplicate.status_code == 200
        assert duplicate.json == response.json
        assert db.session.query(models.Discovery).count() == 1

    @pytest.mark.parametrize("target", ["work", "artist"])
    def test_same_target_can_be_discovered_by_different_users(self, client, target):
        if target == "work":
            work = models.Work(title="A shared work", media_type=models.WorkMediaType.BOOK)
            db.session.add(work)
            db.session.flush()
            payload = {"workId": work.id}
        else:
            payload = {"artistId": artist_factories.ArtistFactory().id}
        first_user = users_factories.UserFactory()
        second_user = users_factories.UserFactory()

        first_response = client.with_token(first_user).post("/native/v1/discoveries", json=payload)
        second_response = client.with_token(second_user).post("/native/v1/discoveries", json=payload)

        assert first_response.status_code == second_response.status_code == 200
        assert first_response.json["id"] != second_response.json["id"]
        assert db.session.query(models.Discovery).count() == 2

    def test_offer_without_work_returns_400(self, client):
        offer = offers_factories.OfferFactory()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"offerId": offer.id})

        assert response.status_code == 400
        assert "offerId" in response.json
        assert db.session.query(models.Discovery).count() == 0

    @pytest.mark.parametrize("payload", [{"workId": 999999999}, {"artistId": "missing"}, {"offerId": 999999999}])
    def test_unknown_target_returns_404(self, client, payload):
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json=payload)

        assert response.status_code == 404

    @pytest.mark.parametrize("payload", [{}, {"workId": 1, "artistId": "artist"}, {"offerId": 1, "workId": 1}])
    def test_invalid_target_combination(self, client, payload):
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json=payload)

        assert response.status_code == 400

    def test_authentication_required(self, client):
        response = client.post("/native/v1/discoveries", json={"workId": 1})

        assert response.status_code == 401


class GetUserDiscoveriesTest:
    @pytest.mark.parametrize("page,limit,expected_days", [(1, 20, [4, 3, 2, 1]), (2, 2, [2, 1])])
    def test_pagination_user_isolation_and_no_n_plus_one(self, client, page, limit, expected_days):
        user = users_factories.UserFactory()
        other_user = users_factories.UserFactory()
        discoveries = []
        for day in range(1, 5):
            artist = artist_factories.ArtistFactory()
            work = models.Work(title=f"Book {day}", media_type=models.WorkMediaType.BOOK)
            db.session.add(models.WorkArtist(work=work, artist=artist, role="author"))
            discovery = models.Discovery(user=user, work=work, discovery_date=date(2026, 10, day))
            db.session.add(discovery)
            discoveries.append(discovery)
        db.session.add(models.Discovery(user=other_user, artist=artist_factories.ArtistFactory()))
        db.session.flush()
        expected_ids = [discoveries[day - 1].id for day in expected_days]
        client.with_token(user)
        db.session.expire_all()

        with assert_num_queries(3):
            response = client.get(f"/native/v1/users/me/discoveries?page={page}&limit={limit}")
            assert response.status_code == 200

        assert response.json["page"] == page
        assert response.json["limit"] == limit
        assert [discovery["id"] for discovery in response.json["discoveries"]] == expected_ids
        assert all(discovery["work"]["mainArtist"] for discovery in response.json["discoveries"])

    def test_artist_discovery_is_listed(self, client):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory(main_role="performer")
        db.session.add(models.Discovery(user=user, artist=artist))
        db.session.flush()
        client.with_token(user)

        response = client.get("/native/v1/users/me/discoveries")

        assert response.status_code == 200
        discovery = response.json["discoveries"][0]
        assert discovery["work"] is None
        assert discovery["artist"] == {"id": artist.id, "name": artist.name, "mainRole": "performer"}

    def test_empty_list(self, client):
        client.with_token(users_factories.UserFactory())

        response = client.get("/native/v1/users/me/discoveries")

        assert response.status_code == 200
        assert response.json == {"page": 1, "limit": 20, "discoveries": []}

    @pytest.mark.parametrize("query", ["page=0", "limit=0", "limit=101", "page=invalid"])
    def test_invalid_pagination(self, client, query):
        client.with_token(users_factories.UserFactory())

        response = client.get(f"/native/v1/users/me/discoveries?{query}")

        assert response.status_code == 400

    def test_authentication_required(self, client):
        response = client.get("/native/v1/users/me/discoveries")

        assert response.status_code == 401
