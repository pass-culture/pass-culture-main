from datetime import date
from datetime import datetime

import pytest
import sqlalchemy as sa
import time_machine

from pcapi import db_utils
from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.discoveries import models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class DiscoveryTest:
    def test_database_cleanup_respects_discovery_dependencies(self, mocker):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory()
        work = models.Work(title="A work to clean", media_type=models.WorkMediaType.BOOK)
        product = offers_factories.ProductFactory(work=work)
        offer = offers_factories.OfferFactory(product=product)
        db.session.add_all(
            [
                models.WorkArtist(work=work, artist=artist, role="author"),
                models.Discovery(user=user, work=work, offer_origin=offer),
                models.Discovery(user=user, artist=artist),
            ]
        )
        db.session.flush()
        models_to_clean = {
            models.Discovery,
            models.WorkArtist,
            models.Work,
            artist_models.Artist,
            offers_models.Offer,
            offers_models.Product,
            users_models.User,
        }
        mocker.patch.object(
            db_utils, "tables_to_clean", [model for model in db_utils.tables_to_clean if model in models_to_clean]
        )
        mocker.patch.object(db_utils, "install_feature_flags")
        mocker.patch.object(db_utils, "install_local_providers")
        mocker.patch.object(db_utils.perm_models, "sync_db_permissions")
        mocker.patch.object(db_utils.perm_models, "sync_db_roles")

        db_utils.clean_all_database()

        for model in models_to_clean:
            assert db.session.query(model).count() == 0

    @pytest.mark.parametrize("target", ["work", "artist"])
    def test_database_rejects_duplicate_target_for_user(self, target):
        user = users_factories.UserFactory()
        if target == "work":
            work = models.Work(title="Unique work", media_type=models.WorkMediaType.BOOK)
            db.session.add(work)
            discovery_target = {"work": work}
        else:
            discovery_target = {"artist": artist_factories.ArtistFactory()}
        db.session.add(models.Discovery(user=user, **discovery_target))
        db.session.flush()

        with db.session.begin_nested():
            db.session.add(models.Discovery(user=user, **discovery_target))
            with pytest.raises(sa.exc.IntegrityError) as error:
                db.session.flush()
            assert error.value.orig.diag.constraint_name == f"ix_unique_discovery_user_{target}"

    @pytest.mark.parametrize("has_work,has_artist", [(True, False), (False, True), (False, False), (True, True)])
    def test_exactly_one_target(self, has_work, has_artist):
        user = users_factories.UserFactory()
        work = models.Work(title="A work", media_type=models.WorkMediaType.BOOK)
        artist = artist_factories.ArtistFactory()
        db.session.add(work)
        db.session.flush()

        discovery = models.Discovery(
            user_id=user.id,
            work_id=work.id if has_work else None,
            artist_id=artist.id if has_artist else None,
        )
        with db.session.begin_nested():
            db.session.add(discovery)
            if has_work != has_artist:
                db.session.flush()
                assert discovery in user.discoveries
            else:
                with pytest.raises(sa.exc.IntegrityError) as error:
                    db.session.flush()
                assert error.value.orig.diag.constraint_name == "check_discovery_exactly_one_target"

    @time_machine.travel("2026-10-13 12:00:00", tick=False)
    def test_defaults_without_offer_origin(self):
        discovery = models.Discovery(user=users_factories.UserFactory(), artist=artist_factories.ArtistFactory())
        db.session.add(discovery)
        db.session.flush()

        assert discovery.discovery_date == date(2026, 10, 13)
        assert discovery.created_at == datetime(2026, 10, 13, 12)
        assert discovery.offer_origin_id is None
        assert discovery.format_context is None
        assert discovery.comment is None
        assert discovery.emotions is None

    def test_work_product_artist_and_offer_relationships(self):
        artist = artist_factories.ArtistFactory(main_role="author", external_ids={"openlibrary_id": "OL1A"})
        work = models.Work(
            title="A work", media_type=models.WorkMediaType.BOOK, external_ids={"openlibrary_id": "OL1W"}
        )
        link = models.WorkArtist(work=work, artist=artist, role="author")
        product = offers_factories.ProductFactory(work=work)
        offer = offers_factories.OfferFactory(product=product)
        user = users_factories.UserFactory()
        discovery = models.Discovery(
            user=user,
            work=work,
            offer_origin=offer,
            format_context="read",
            emotions=[models.DiscoveryEmotion.MOVED.value],
        )
        db.session.add_all([link, discovery])
        db.session.flush()
        db.session.expire_all()

        assert discovery.user == user
        assert discovery in user.discoveries
        assert discovery in work.discoveries
        assert discovery.offer_origin == offer
        assert product.work == work
        assert product in work.products
        assert link in work.artist_links
        assert link in artist.work_links
        assert link.role == "author"
        assert artist.external_ids == {"openlibrary_id": "OL1A"}
        assert work.external_ids == {"openlibrary_id": "OL1W"}

    def test_external_ids_default_and_in_place_changes(self):
        work = models.Work(title="A film", media_type=models.WorkMediaType.FILM)
        db.session.add(work)
        db.session.flush()
        assert work.external_ids == {}

        work.external_ids["tmdb_id"] = 123
        db.session.flush()
        db.session.expire(work)
        assert work.external_ids == {"tmdb_id": 123}
