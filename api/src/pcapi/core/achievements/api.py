import datetime

from pcapi.core.achievements import exceptions as achievements_exceptions
from pcapi.core.achievements import models as achievements_models
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.users import models as users_models
from pcapi.models import db


def unlock_achievement(booking: bookings_models.Booking) -> achievements_models.Achievement | None:
    """
    Flushes and returns an achievement corresponding to the booking subcategory if the achievement was
    not previously unlocked.

    This function assumes the following relationships are already loaded to avoid additional queries:
    - booking.user.achievements.name
    - booking.stock.offer.subcategoryId

    Example: db.session.query(Booking)
             .options(joinedload(Booking.user).selectinload(User.achievements))
             .options(joinedload(Booking.stock).joinedload(Stock.offer))
    """
    achievement_name = _get_booking_achievement(booking)
    if not achievement_name:
        return None

    previously_unlocked_achievement_names = [
        unlocked_achievement.name for unlocked_achievement in booking.user.achievements
    ]
    if achievement_name in previously_unlocked_achievement_names:
        return None

    achievement = achievements_models.Achievement(user=booking.user, booking=booking, name=achievement_name)
    db.session.add(achievement)
    db.session.flush()

    return achievement


ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS = {
    achievements_models.AchievementEnum.FIRST_MOVIE_BOOKING: [
        subcategories.SEANCE_CINE.id,
        subcategories.CINE_PLEIN_AIR.id,
    ],
    achievements_models.AchievementEnum.FIRST_BOOK_BOOKING: [subcategories.LIVRE_PAPIER.id],
    achievements_models.AchievementEnum.FIRST_RECORDED_MUSIC_BOOKING: [
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    ],
    achievements_models.AchievementEnum.FIRST_SHOW_BOOKING: [
        subcategories.SPECTACLE_REPRESENTATION.id,
        subcategories.SPECTACLE_VENTE_DISTANCE.id,
        subcategories.ABO_SPECTACLE.id,
        subcategories.FESTIVAL_SPECTACLE.id,
    ],
    achievements_models.AchievementEnum.FIRST_MUSEUM_BOOKING: [
        subcategories.VISITE.id,
        subcategories.CARTE_MUSEE.id,
        subcategories.MUSEE_VENTE_DISTANCE.id,
        subcategories.VISITE_GUIDEE.id,
        subcategories.CONFERENCE.id,
        subcategories.EVENEMENT_PATRIMOINE.id,
    ],
    achievements_models.AchievementEnum.FIRST_LIVE_MUSIC_BOOKING: [
        subcategories.CONCERT.id,
        subcategories.FESTIVAL_MUSIQUE.id,
        subcategories.ABO_CONCERT.id,
        subcategories.EVENEMENT_MUSIQUE.id,
    ],
    achievements_models.AchievementEnum.FIRST_NEWS_BOOKING: [subcategories.ABO_PRESSE_EN_LIGNE.id],
    achievements_models.AchievementEnum.FIRST_INSTRUMENT_BOOKING: [
        subcategories.ACHAT_INSTRUMENT.id,
        subcategories.BON_ACHAT_INSTRUMENT.id,
        subcategories.PARTITION.id,
        subcategories.MATERIEL_ART_CREATIF.id,
    ],
    achievements_models.AchievementEnum.FIRST_ART_LESSON_BOOKING: [
        subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
        subcategories.ATELIER_PRATIQUE_ART.id,
        subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id,
        subcategories.ABO_PRATIQUE_ART.id,
        subcategories.PRATIQUE_ART_VENTE_DISTANCE.id,
    ],
}


def _get_booking_achievement(booking: bookings_models.Booking) -> achievements_models.AchievementEnum | None:
    for achievement_name, subcategory_ids in ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS.items():
        if booking.stock.offer.subcategoryId in subcategory_ids:
            return achievement_name

    return None


def mark_achievements_as_seen(user: users_models.User, achievement_ids: list[int]) -> None:
    achievements = [achievement for achievement in user.achievements if achievement.id in achievement_ids]

    if len(achievements) != len(achievement_ids):
        raise achievements_exceptions.AchievementNotFound(
            f"Some {achievement_ids = } were not found for user {user.id}"
        )

    for achievement in achievements:
        achievement.seenDate = datetime.datetime.utcnow()

    db.session.flush()
