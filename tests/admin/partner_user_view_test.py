from wtforms import Form

from pcapi.admin.custom_views.partner_user_view import PartnerUserView
from pcapi.core.users.models import User


class PartnerUserViewTest:
    def test_should_generate_a_random_password_and_token_on_creation(self, app, db_session):
        # given
        user = User()
        user.password = None
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=True)

        # then
        assert user.password is not None
        assert user.resetPasswordToken is not None

    def test_should_preserve_password_on_edition(self, app, db_session):
        # given
        user = User()
        user.password = "OriginalPassword"
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.password == "OriginalPassword"

    def test_a_partner_should_never_be_a_beneficiary(self, app, db_session):
        # given
        user = User()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.isBeneficiary == False

    def test_a_partner_should_never_be_an_admin(self, app, db_session):
        # given
        user = User()
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.isAdmin == False

    def test_should_create_the_public_name(self, app, db_session):
        # given
        user = User()
        user.firstName = "Ken"
        user.lastName = "Thompson"
        user.publicName = None
        view = PartnerUserView(model=User, session=db_session)

        # when
        view.on_model_change(Form(), model=user, is_created=False)

        # then
        assert user.publicName == "Ken Thompson"
