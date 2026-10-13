from datetime import date

import pytest
import sqlalchemy as sa

from pcapi.core.artist import factories as artist_factories
from pcapi.core.discoveries import models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class CreateDiscoveryTest:
    def test_sentiment_is_no_longer_accepted(self, client):
        artist = artist_factories.ArtistFactory()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"artistId": artist.id, "sentiment": "liked"})

        assert response.status_code == 400
        assert db.session.query(models.Discovery).count() == 0

    @pytest.mark.parametrize("target", ["work", "artist", "offer"])
    @pytest.mark.parametrize(
        "emotion",
        [[member.value] for member in models.DiscoveryEmotion] + [[member.value for member in models.DiscoveryEmotion]],
    )
    def test_comment_and_emotion_are_persisted_and_listed(self, client, target, emotion):
        user = users_factories.UserFactory()
        if target == "artist":
            payload = {"artistId": artist_factories.ArtistFactory().id}
        else:
            work = models.Work(title="A work", media_type=models.WorkMediaType.BOOK)
            product = offers_factories.ProductFactory(work=work)
            if target == "offer":
                payload = {"offerId": offers_factories.OfferFactory(product=product).id}
            else:
                payload = {"workId": work.id}
        payload.update({"comment": "Une rencontre qui fait r\u00e9fl\u00e9chir.", "emotions": emotion})
        client.with_token(user)

        response = client.post("/native/v1/discoveries", json=payload)

        assert response.status_code == 200
        assert response.json["comment"] == payload["comment"]
        assert response.json["emotions"] == emotion
        db.session.expire_all()
        discovery = db.session.query(models.Discovery).one()
        assert discovery.comment == payload["comment"]
        assert discovery.emotions == emotion
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert listing.json["discoveries"][0]["comment"] == payload["comment"]
        assert listing.json["discoveries"][0]["emotions"] == emotion

    @pytest.mark.parametrize("emotion", ["happy", "", "intrigue", ["surpris", "happy"]])
    def test_unknown_emotion_returns_400(self, client, emotion):
        artist = artist_factories.ArtistFactory()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"artistId": artist.id, "emotions": emotion})

        assert response.status_code == 400
        assert db.session.query(models.Discovery).count() == 0

    def test_singular_emotion_key_is_rejected(self, client):
        artist = artist_factories.ArtistFactory()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"artistId": artist.id, "emotion": ["touch\u00e9"]})

        assert response.status_code == 400
        assert db.session.query(models.Discovery).count() == 0

    def test_database_rejects_unknown_emotion(self):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory()

        with pytest.raises(sa.exc.IntegrityError) as error:
            with db.session.begin_nested():
                db.session.execute(
                    sa.insert(models.Discovery).values(user_id=user.id, artist_id=artist.id, emotions=["happy"])
                )
        assert error.value.orig.diag.constraint_name == "check_discovery_emotions"

    def test_work_is_idempotent(self, client):
        user = users_factories.UserFactory()
        work = models.Work(title="A book", media_type=models.WorkMediaType.BOOK)
        db.session.add(work)
        db.session.flush()
        client.with_token(user)
        payload = {
            "workId": work.id,
            "discoveryDate": "2026-10-12",
            "formatContext": "read",
            "comment": "My original comment",
            "emotions": ["surpris"],
        }

        response = client.post("/native/v1/discoveries", json=payload)
        duplicate = client.post(
            "/native/v1/discoveries",
            json={"workId": work.id, "comment": "Changed comment", "emotions": ["touch\u00e9"]},
        )

        assert response.status_code == 200
        assert duplicate.status_code == 200
        assert response.json == duplicate.json
        assert response.json["work"]["title"] == "A book"
        assert response.json["discoveryDate"] == "2026-10-12"
        assert response.json["artist"] is None
        assert response.json["comment"] == "My original comment"
        assert response.json["emotions"] == ["surpris"]
        assert "sentiment" not in response.json
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert "sentiment" not in listing.json["discoveries"][0]
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
        assert response.json["comment"] is None
        assert response.json["emotions"] is None
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

    def test_offer_without_product_resolves_direct_work(self, client):
        offer = offers_factories.OfferFactory(name="A standalone offer")
        work = models.Work(title=offer.name, media_type=models.WorkMediaType.OTHER, offer=offer)
        db.session.add(work)
        db.session.flush()
        client.with_token(users_factories.UserFactory())

        response = client.post("/native/v1/discoveries", json={"offerId": offer.id})

        assert response.status_code == 200
        assert response.json["workId"] == work.id
        assert response.json["offerOriginId"] == offer.id
        assert response.json["work"]["title"] == offer.name

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


class UpdateDiscoveryTest:
    @pytest.mark.parametrize("date_field", ["discoveryDate", "discovery_date"])
    def test_updates_discovery_date_and_listing_order(self, client, date_field):
        user = users_factories.UserFactory()
        discovery = models.Discovery(
            user=user,
            artist=artist_factories.ArtistFactory(),
            discovery_date=date(2026, 10, 12),
            comment="Original",
            emotions=[models.DiscoveryEmotion.SURPRISED.value],
        )
        other_discovery = models.Discovery(
            user=user, artist=artist_factories.ArtistFactory(), discovery_date=date(2026, 10, 11)
        )
        db.session.add_all([discovery, other_discovery])
        db.session.flush()
        discovery_id = discovery.id
        other_id = other_discovery.id
        original_created_at = discovery.created_at
        client.with_token(user)

        response = client.patch(f"/native/v1/discoveries/{discovery_id}", json={date_field: "2026-10-10"})

        assert response.status_code == 200
        assert response.json["discoveryDate"] == "2026-10-10"
        assert response.json["comment"] == "Original"
        assert response.json["emotions"] == ["surpris"]
        db.session.expire_all()
        assert discovery.discovery_date == date(2026, 10, 10)
        assert discovery.created_at == original_created_at
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert [item["id"] for item in listing.json["discoveries"]] == [other_id, discovery_id]
        assert listing.json["discoveries"][1]["discoveryDate"] == "2026-10-10"

    @pytest.mark.parametrize("target", ["work", "artist"])
    @pytest.mark.parametrize(
        "emotion",
        [[member.value] for member in models.DiscoveryEmotion] + [[member.value for member in models.DiscoveryEmotion]],
    )
    def test_updates_comment_and_emotion(self, client, target, emotion):
        user = users_factories.UserFactory()
        if target == "work":
            work = models.Work(title="A work", media_type=models.WorkMediaType.BOOK)
            discovery = models.Discovery(user=user, work=work)
        else:
            discovery = models.Discovery(user=user, artist=artist_factories.ArtistFactory())
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        client.with_token(user)

        response = client.patch(
            f"/native/v1/discoveries/{discovery_id}", json={"comment": "A new comment", "emotions": emotion}
        )

        assert response.status_code == 200
        assert response.json["id"] == discovery_id
        assert response.json["comment"] == "A new comment"
        assert response.json["emotions"] == emotion
        db.session.expire_all()
        assert discovery.comment == "A new comment"
        assert discovery.emotions == emotion
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert listing.json["discoveries"][0]["comment"] == "A new comment"
        assert listing.json["discoveries"][0]["emotions"] == emotion
        assert db.session.query(models.Discovery).count() == 1

    @pytest.mark.parametrize(
        "payload,expected_comment,expected_emotion",
        [
            ({"comment": "Updated"}, "Updated", ["surpris"]),
            ({"emotions": ["touch\u00e9"]}, "Original", ["touch\u00e9"]),
            ({"comment": None}, None, ["surpris"]),
            ({"emotions": None}, "Original", None),
            ({"comment": None, "emotions": None}, None, None),
            ({}, "Original", ["surpris"]),
        ],
    )
    def test_partial_updates_and_null_fields(self, client, payload, expected_comment, expected_emotion):
        user = users_factories.UserFactory()
        discovery = models.Discovery(
            user=user,
            artist=artist_factories.ArtistFactory(),
            comment="Original",
            emotions=[models.DiscoveryEmotion.SURPRISED.value],
        )
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        original_artist_id = discovery.artist_id
        original_date = discovery.discovery_date
        original_created_at = discovery.created_at
        client.with_token(user)

        response = client.patch(f"/native/v1/discoveries/{discovery_id}", json=payload)

        assert response.status_code == 200
        assert response.json["comment"] == expected_comment
        assert response.json["emotions"] == expected_emotion
        assert "sentiment" not in response.json
        db.session.expire_all()
        assert discovery.comment == expected_comment
        assert discovery.emotions == expected_emotion
        assert discovery.artist_id == original_artist_id
        assert discovery.discovery_date == original_date
        assert discovery.created_at == original_created_at

    def test_cannot_update_another_users_discovery(self, client):
        discovery = models.Discovery(
            user=users_factories.UserFactory(), artist=artist_factories.ArtistFactory(), comment="Original"
        )
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        client.with_token(users_factories.UserFactory())

        response = client.patch(f"/native/v1/discoveries/{discovery_id}", json={"comment": "Changed"})

        assert response.status_code == 404
        db.session.expire_all()
        assert discovery.comment == "Original"

    def test_unknown_discovery_returns_404(self, client):
        client.with_token(users_factories.UserFactory())

        response = client.patch("/native/v1/discoveries/999999999", json={"comment": "Changed"})

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "payload",
        [
            {"emotions": "happy"},
            {"comment": 42},
            {"userId": 1},
            {"workId": 1},
            {"sentiment": "changed"},
            {"discoveryDate": None},
            {"discoveryDate": "invalid"},
            {"discoveryDate": "2026-02-30"},
        ],
    )
    def test_invalid_update_returns_400_without_changing_discovery(self, client, payload):
        user = users_factories.UserFactory()
        discovery = models.Discovery(user=user, artist=artist_factories.ArtistFactory(), comment="Original")
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        original_date = discovery.discovery_date
        client.with_token(user)

        response = client.patch(f"/native/v1/discoveries/{discovery_id}", json=payload)

        assert response.status_code == 400
        db.session.expire_all()
        assert discovery.comment == "Original"
        assert discovery.emotions is None
        assert discovery.discovery_date == original_date

    def test_authentication_required(self, client):
        response = client.patch("/native/v1/discoveries/1", json={"comment": "Changed"})

        assert response.status_code == 401


class DeleteDiscoveryTest:
    @pytest.mark.parametrize("target", ["work", "artist"])
    def test_deletes_discovery_without_deleting_target_and_can_create_it_again(self, client, target):
        user = users_factories.UserFactory()
        if target == "work":
            cultural_target = models.Work(title="A work", media_type=models.WorkMediaType.BOOK)
            discovery = models.Discovery(user=user, work=cultural_target)
        else:
            cultural_target = artist_factories.ArtistFactory()
            discovery = models.Discovery(user=user, artist=cultural_target)
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        target_id = cultural_target.id
        client.with_token(user)

        response = client.delete(f"/native/v1/discoveries/{discovery_id}")

        assert response.status_code == 204
        assert response.data == b""
        assert db.session.query(models.Discovery).count() == 0
        assert db.session.query(type(cultural_target)).filter_by(id=target_id).count() == 1
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert listing.json["discoveries"] == []
        recreated = client.post("/native/v1/discoveries", json={f"{target}Id": target_id})
        assert recreated.status_code == 200
        assert recreated.json["id"] != discovery_id
        assert db.session.query(models.Discovery).count() == 1

    def test_cannot_delete_another_users_discovery(self, client):
        discovery = models.Discovery(user=users_factories.UserFactory(), artist=artist_factories.ArtistFactory())
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        client.with_token(users_factories.UserFactory())

        response = client.delete(f"/native/v1/discoveries/{discovery_id}")

        assert response.status_code == 404
        assert db.session.query(models.Discovery).filter_by(id=discovery_id).count() == 1

    def test_unknown_discovery_returns_404(self, client):
        client.with_token(users_factories.UserFactory())

        response = client.delete("/native/v1/discoveries/999999999")

        assert response.status_code == 404

    def test_second_delete_returns_404(self, client):
        user = users_factories.UserFactory()
        discovery = models.Discovery(user=user, artist=artist_factories.ArtistFactory())
        db.session.add(discovery)
        db.session.flush()
        discovery_id = discovery.id
        client.with_token(user)

        assert client.delete(f"/native/v1/discoveries/{discovery_id}").status_code == 204
        assert client.delete(f"/native/v1/discoveries/{discovery_id}").status_code == 404

    def test_authentication_required(self, client):
        response = client.delete("/native/v1/discoveries/1")

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
