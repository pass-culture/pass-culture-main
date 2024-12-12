from pcapi.core.achievements import models as achievements_models
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
from pcapi.models import db


def unlock_achievement(booking: bookings_models.Booking) -> achievements_models.Achievement | None:
    """
    Flushes and returns an achievement corresponding to the booking subcategory if the achievement was
    not previously unlocked.

    This function assumes the following relationships are already loaded to avoid additional queries:
    - booking.user.achievements.name
    - booking.stock.offer.subcategoryId

    Example: Booking.query
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
        subcategories_v2.SEANCE_CINE.id,
        subcategories_v2.CINE_PLEIN_AIR.id,
    ],
    achievements_models.AchievementEnum.FIRST_BOOK_BOOKING: [subcategories_v2.LIVRE_PAPIER.id],
    achievements_models.AchievementEnum.FIRST_RECORDED_MUSIC_BOOKING: [
        subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    ],
    achievements_models.AchievementEnum.FIRST_SHOW_BOOKING: [
        subcategories_v2.SPECTACLE_REPRESENTATION.id,
        subcategories_v2.SPECTACLE_VENTE_DISTANCE.id,
        subcategories_v2.ABO_SPECTACLE.id,
        subcategories_v2.FESTIVAL_SPECTACLE.id,
    ],
    achievements_models.AchievementEnum.FIRST_MUSEUM_BOOKING: [
        subcategories_v2.VISITE.id,
        subcategories_v2.CARTE_MUSEE.id,
        subcategories_v2.MUSEE_VENTE_DISTANCE.id,
        subcategories_v2.VISITE_GUIDEE.id,
        subcategories_v2.CONFERENCE.id,
        subcategories_v2.EVENEMENT_PATRIMOINE.id,
    ],
    achievements_models.AchievementEnum.FIRST_LIVE_MUSIC_BOOKING: [
        subcategories_v2.CONCERT.id,
        subcategories_v2.FESTIVAL_MUSIQUE.id,
        subcategories_v2.ABO_CONCERT.id,
        subcategories_v2.EVENEMENT_MUSIQUE.id,
    ],
    achievements_models.AchievementEnum.FIRST_NEWS_BOOKING: [subcategories_v2.ABO_PRESSE_EN_LIGNE.id],
    achievements_models.AchievementEnum.FIRST_INSTRUMENT_BOOKING: [
        subcategories_v2.ACHAT_INSTRUMENT.id,
        subcategories_v2.BON_ACHAT_INSTRUMENT.id,
        subcategories_v2.PARTITION.id,
        subcategories_v2.MATERIEL_ART_CREATIF.id,
    ],
    achievements_models.AchievementEnum.FIRST_ART_LESSON_BOOKING: [
        subcategories_v2.SEANCE_ESSAI_PRATIQUE_ART.id,
        subcategories_v2.ATELIER_PRATIQUE_ART.id,
        subcategories_v2.PLATEFORME_PRATIQUE_ARTISTIQUE.id,
        subcategories_v2.ABO_PRATIQUE_ART.id,
        subcategories_v2.PRATIQUE_ART_VENTE_DISTANCE.id,
    ],
}


def _get_booking_achievement(booking: bookings_models.Booking) -> achievements_models.AchievementEnum | None:
    for achievement_name, subcategory_ids in ACHIEVEMENT_NAME_TO_SUBCATEGORY_IDS.items():
        if booking.stock.offer.subcategoryId in subcategory_ids:
            return achievement_name

    return None
