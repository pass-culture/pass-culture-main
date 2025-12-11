import pytest

from pcapi.core.achievements import factories as achievements_factories
from pcapi.core.achievements import models as achievements_models
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class MarkAchievementsAsSeenTest:
    def test_mark_achievements_as_seen(self, client):
        user = users_factories.BeneficiaryFactory()
        achievement_1 = achievements_factories.AchievementFactory(
            user=user, name=achievements_models.AchievementEnum.FIRST_ART_LESSON_BOOKING
        )
        achievement_2 = achievements_factories.AchievementFactory(
            user=user, name=achievements_models.AchievementEnum.FIRST_BOOK_BOOKING
        )
        unseen_achievement = achievements_factories.AchievementFactory(
            user=user, name=achievements_models.AchievementEnum.FIRST_LIVE_MUSIC_BOOKING
        )

        response = client.with_token(user).post(
            "/native/v1/achievements/mark_as_seen", json={"achievementIds": [achievement_1.id, achievement_2.id]}
        )

        assert response.status_code == 200, response.json
        assert achievement_1.seenDate is not None
        assert achievement_2.seenDate is not None
        assert unseen_achievement.seenDate is None

    def test_achievement_not_found(self, client):
        user = users_factories.BeneficiaryFactory()

        response = client.with_token(user).post("/native/v1/achievements/mark_as_seen", json={"achievementIds": [1]})

        assert response.status_code == 404, response.json
        assert response.json["code"] == "ACHIEVEMENT_NOT_FOUND"

    def test_client_not_logged_in(self, client):
        response = client.post("/native/v1/achievements/mark_as_seen", json={"achievementIds": []})

        assert response.status_code == 401, response.json
