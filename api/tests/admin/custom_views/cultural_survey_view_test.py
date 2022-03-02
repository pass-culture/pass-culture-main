import pcapi.core.users.factories as users_factories


class CulturalSurveyViewTest:
    def test_authorized_user(self, app, db_session, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        client.with_session_auth(admin.email)

        response = client.get("/pc/back-office/cultural_survey_answers")

        assert response.status_code == 200

    def test_unauthorized_user(self, app, db_session, client):
        user = users_factories.UserFactory(email="admin@example.com")
        client.with_session_auth(user.email)

        response = client.get("/pc/back-office/cultural_survey_answers")

        assert response.status_code == 403
