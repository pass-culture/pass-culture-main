from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


class Returns200Test:
    @override_features(WIP_CONNECT_AS=True)
    def test_current_user_has_rights_to_impersonate_a_pro(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        expected_num_queries = 8
        # session
        # user
        # feature
        # user
        # INSERT INTO action_history
        # DELETE FROM user_session
        # user
        # INSERT INTO user_session
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 302

        # then
        assert response.location == expected_redirect_link
        # check user is impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == target.id
            assert session["_user_id"] == str(target.id)
            assert session["internal_admin_email"] == admin.email
            assert session["internal_admin_id"] == admin.id

    @override_features(WIP_CONNECT_AS=True)
    def test_current_user_has_rights_to_impersonate_a_non_attached_pro(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        expected_num_queries = 8
        # session
        # user
        # feature
        # user
        # INSERT INTO action_history
        # DELETE FROM user_session
        # user
        # INSERT INTO user_session
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 302

        # then

        assert response.location == expected_redirect_link
        # check user is impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == target.id
            assert session["_user_id"] == str(target.id)
            assert session["internal_admin_email"] == admin.email
            assert session["internal_admin_id"] == admin.id

    @override_features(WIP_CONNECT_AS=True)
    def test_current_user_already_impersonnating_a_pro(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        intermediary_target = users_factories.ProFactory()
        real_target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        intermediary_secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=intermediary_target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        real_secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=real_target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )

        # use connect as to connect to a pro
        client = client.with_session_auth(admin.email)
        expected_num_queries = 8
        # session
        # user
        # feature
        # user
        # INSERT INTO action_history
        # DELETE FROM user_session
        # user
        # INSERT INTO user_session
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/users/connect-as/{intermediary_secure_token.token}")
            assert response.status_code == 302

        assert response.location == expected_redirect_link

        # when
        client = client.with_session_auth(admin.email)
        expected_num_queries = 8
        # session
        # user
        # feature
        # user
        # INSERT INTO action_history
        # DELETE FROM user_session
        # user
        # INSERT INTO user_session
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/users/connect-as/{real_secure_token.token}")
            assert response.status_code == 302

        assert response.location == expected_redirect_link

        # then
        assert response.status_code == 302
        assert response.location == expected_redirect_link
        # check user is impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == real_target.id
            assert session["_user_id"] == str(real_target.id)
            assert session["internal_admin_email"] == admin.email
            assert session["internal_admin_id"] == admin.id


class Returns401Test:
    @override_features(WIP_CONNECT_AS=True)
    def test_user_not_connected(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        with assert_num_queries(0):
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 401

        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert "user_id" not in session
            assert "_user_id" not in session
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session


class Returns403Test:
    @override_features(WIP_CONNECT_AS=True)
    def test_user_is_not_admin(self, client, db_session):
        # given
        admin = users_factories.UserFactory(email="admin@example.com")
        target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(3):  #  session + user + feature
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {
            "global": "L'utilisateur doit être connecté avec un compte admin pour pouvoir utiliser cet endpoint",
        }
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_token_is_invalid(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        token = "xROk-l708o7G5gWf3BBVlHOviiVPODGDHxCBbCHcycLFI8n3yaCgQcUGH0WYSq3ROXU2DD7P-pyLKNdQjcKNFg"  # ggignore

        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(3):  #  session + user + feature
            response = client.get(f"/users/connect-as/{token}")
            assert response.status_code == 403

        # then
        assert response.json == {"global": "Le token est invalide"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_token_is_for_other_admin(self, client, db_session):
        # given
        admin = users_factories.AdminFactory()
        target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=0,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(3):  #  session + user + feature
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {"global": "Le token a été généré pour un autre admin"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_user_is_not_active(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory(isActive=False)

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(4):  #  session + user + feature + user
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {"user": "L'utilisateur est inactif"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_user_is_admin(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.AdminFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(4):  #  session + user + feature + user
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {"user": "L'utilisateur est un admin"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_user_is_anonymous(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory(roles=[users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED])

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(4):  #  session + user + feature + user
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {"user": "L'utilisateur est anonyme"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=True)
    def test_user_is_not_pro(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.BeneficiaryGrant18Factory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(4):  #  session + user + feature + user
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 403

        # then
        assert response.json == {"user": "L'utilisateur n'est pas un pro"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session


class Returns404Test:
    @override_features(WIP_CONNECT_AS=True)
    def test_user_not_found(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=0,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(4):  #  session + user + feature + user
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 404

        # then
        assert response.json == {"user": "L'utilisateur demandé n'existe pas"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session

    @override_features(WIP_CONNECT_AS=False)
    def test_current_user_has_rights_to_impersonate_a_pro(self, client, db_session):
        # given
        admin = users_factories.AdminFactory(email="admin@example.com")
        target = users_factories.ProFactory()

        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=target.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        # when
        client = client.with_session_auth(admin.email)
        with assert_num_queries(3):  # session + user + feature
            response = client.get(f"/users/connect-as/{secure_token.token}")
            assert response.status_code == 404

        # then
        assert response.json == {"global": "La route n'est pas active"}
        # check user is not impersonated
        with client.client.session_transaction() as session:
            assert session["user_id"] == admin.id
            assert session["_user_id"] == str(admin.id)
            assert "internal_admin_email" not in session
            assert "internal_admin_id" not in session
