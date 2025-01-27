import pytest

from pcapi.core.achievements import api as achievements_api
from pcapi.core.achievements import models as achievements_models
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class AchievementUnlockTest:
    @pytest.mark.parametrize("movie_subcategory_id", [subcategories.SEANCE_CINE.id, subcategories.CINE_PLEIN_AIR.id])
    def test_movie_booking_achievement_unlock(self, movie_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        movie_booking = bookings_factories.BookingFactory(user=user, stock__offer__subcategoryId=movie_subcategory_id)

        achievements_api.unlock_achievement(movie_booking)

        (achievement,) = user.achievements
        assert achievement.booking == movie_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_MOVIE_BOOKING

    def test_book_booking_achievement_unlock(self):
        user = users_factories.BeneficiaryGrant18Factory()
        book_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )

        achievements_api.unlock_achievement(book_booking)

        (achievement,) = user.achievements
        assert achievement.booking == book_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_BOOK_BOOKING

    @pytest.mark.parametrize(
        "recorded_music_subcategory_id",
        [subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id],
    )
    def test_recorded_music_booking_achievement_unlock(self, recorded_music_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        recorded_music_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=recorded_music_subcategory_id
        )

        achievements_api.unlock_achievement(recorded_music_booking)

        (achievement,) = user.achievements
        assert achievement.booking == recorded_music_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_RECORDED_MUSIC_BOOKING

    @pytest.mark.parametrize(
        "show_subcategory_id",
        [
            subcategories.SPECTACLE_REPRESENTATION.id,
            subcategories.SPECTACLE_VENTE_DISTANCE.id,
            subcategories.ABO_SPECTACLE.id,
            subcategories.FESTIVAL_SPECTACLE.id,
        ],
    )
    def test_show_booking_achievement_unlock(self, show_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        show_booking = bookings_factories.BookingFactory(user=user, stock__offer__subcategoryId=show_subcategory_id)

        achievements_api.unlock_achievement(show_booking)

        (achievement,) = user.achievements
        assert achievement.booking == show_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_SHOW_BOOKING

    @pytest.mark.parametrize(
        "show_subcategory_id",
        [
            subcategories.SPECTACLE_REPRESENTATION.id,
            subcategories.SPECTACLE_VENTE_DISTANCE.id,
            subcategories.ABO_SPECTACLE.id,
            subcategories.FESTIVAL_SPECTACLE.id,
        ],
    )
    def test_show_booking_achievement_unlock(self, show_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        show_booking = bookings_factories.BookingFactory(user=user, stock__offer__subcategoryId=show_subcategory_id)

        achievements_api.unlock_achievement(show_booking)

        (achievement,) = user.achievements
        assert achievement.booking == show_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_SHOW_BOOKING

    @pytest.mark.parametrize(
        "museum_subcategory_id",
        [
            subcategories.VISITE.id,
            subcategories.CARTE_MUSEE.id,
            subcategories.MUSEE_VENTE_DISTANCE.id,
            subcategories.VISITE_GUIDEE.id,
            subcategories.CONFERENCE.id,
            subcategories.EVENEMENT_PATRIMOINE.id,
        ],
    )
    def test_museum_booking_achievement_unlock(self, museum_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        museum_booking = bookings_factories.BookingFactory(user=user, stock__offer__subcategoryId=museum_subcategory_id)

        achievements_api.unlock_achievement(museum_booking)

        (achievement,) = user.achievements
        assert achievement.booking == museum_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_MUSEUM_BOOKING

    @pytest.mark.parametrize(
        "live_music_subcategory_id",
        [
            subcategories.CONCERT.id,
            subcategories.FESTIVAL_MUSIQUE.id,
            subcategories.ABO_CONCERT.id,
            subcategories.EVENEMENT_MUSIQUE.id,
        ],
    )
    def test_live_music_booking_achievement_unlock(self, live_music_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        live_music_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=live_music_subcategory_id
        )

        achievements_api.unlock_achievement(live_music_booking)

        (achievement,) = user.achievements
        assert achievement.booking == live_music_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_LIVE_MUSIC_BOOKING

    def test_news_booking_achievement_unlock(self):
        user = users_factories.BeneficiaryGrant18Factory()
        news_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id
        )

        achievements_api.unlock_achievement(news_booking)

        (achievement,) = user.achievements
        assert achievement.booking == news_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_NEWS_BOOKING

    @pytest.mark.parametrize(
        "art_lesson_subcategory_id",
        [
            subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            subcategories.ATELIER_PRATIQUE_ART.id,
            subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id,
            subcategories.ABO_PRATIQUE_ART.id,
            subcategories.PRATIQUE_ART_VENTE_DISTANCE.id,
        ],
    )
    def test_art_lesson_booking_achievement_unlock(self, art_lesson_subcategory_id):
        user = users_factories.BeneficiaryGrant18Factory()
        art_lesson_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=art_lesson_subcategory_id
        )

        achievements_api.unlock_achievement(art_lesson_booking)

        (achievement,) = user.achievements
        assert achievement.booking == art_lesson_booking
        assert achievement.name == achievements_models.AchievementEnum.FIRST_ART_LESSON_BOOKING

    def test_booking_without_achievement(self):
        user = users_factories.BeneficiaryGrant18Factory()
        booking_without_achievement = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=subcategories.CONCOURS.id
        )

        achievements_api.unlock_achievement(booking_without_achievement)

        assert not user.achievements

    def test_booking_achievement_idempotence(self):
        user = users_factories.BeneficiaryGrant18Factory()
        book_booking = bookings_factories.BookingFactory(
            user=user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )

        achievements_api.unlock_achievement(book_booking)
        achievements_api.unlock_achievement(book_booking)

        assert len(user.achievements) == 1
