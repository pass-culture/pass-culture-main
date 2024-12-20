from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.achievements.models import AchievementEnum
from pcapi.core.achievements.factories import AchievementFactory
from pcapi.core.bookings.factories import UsedBookingFactory
from pcapi.core.categories.subcategories_v2 import LIVRE_PAPIER
from pcapi.core.categories.subcategories_v2 import FESTIVAL_MUSIQUE
from pcapi.core.categories.subcategories_v2 import PARTITION
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import UnderageBeneficiaryFactory
from pcapi.scripts.achievements.main import unlock_existing_achievements


@pytest.mark.usefixtures("db_session")
class AchievementsUnlockTest:
    def test_achievement_unlocks(self):
        beneficiary = BeneficiaryFactory()
        UsedBookingFactory(user=beneficiary, stock__offer__subcategoryId=FESTIVAL_MUSIQUE.id)

        unlock_existing_achievements()

        assert beneficiary.achievements

    def test_achievement_unlocks_num_queries(self):
        beneficiary_with_new_achievements = BeneficiaryFactory()
        UsedBookingFactory(user=beneficiary_with_new_achievements, stock__offer__subcategoryId=FESTIVAL_MUSIQUE.id)
        UsedBookingFactory(user=beneficiary_with_new_achievements, stock__offer__subcategoryId=LIVRE_PAPIER.id)

        beneficiary_with_new_music_achievement = BeneficiaryFactory()
        AchievementFactory(user=beneficiary_with_new_music_achievement, name=AchievementEnum.FIRST_BOOK_BOOKING)
        UsedBookingFactory(user=beneficiary_with_new_music_achievement, stock__offer__subcategoryId=FESTIVAL_MUSIQUE.id)

        num_queries = (
            1  # select user page
            + 1  # select achievement-winning bookings
            + 1  # select already unlocked achievements
            + 1  # insert new achievements
        )
        with assert_num_queries(num_queries):
            unlock_existing_achievements()

        assert len(beneficiary_with_new_achievements.achievements) == 2
        assert len(beneficiary_with_new_music_achievement.achievements) == 2

    def test_achievement_unlocks_using_earliest_used_booking(self):
        beneficiary = BeneficiaryFactory()
        last_week = datetime.utcnow() - timedelta(weeks=1)
        earliest_used_booking = UsedBookingFactory(
            user=beneficiary, stock__offer__subcategoryId=FESTIVAL_MUSIQUE.id, dateUsed=last_week
        )
        UsedBookingFactory(user=beneficiary, stock__offer__subcategoryId=FESTIVAL_MUSIQUE.id)

        unlock_existing_achievements()

        (achievement,) = beneficiary.achievements
        assert achievement.unlockedDate == earliest_used_booking.dateUsed

    def test_no_achievement(self):
        beneficiary = BeneficiaryFactory()
        UsedBookingFactory(user=beneficiary, stock__offer__subcategoryId=PARTITION.id)

        unlock_existing_achievements()

        assert beneficiary.achievements
