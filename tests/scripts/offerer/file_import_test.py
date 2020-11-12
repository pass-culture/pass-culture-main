from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import UserSQLEntity
from pcapi.repository import repository
from pcapi.scripts.offerer.file_import import OffererNotCreatedException
from pcapi.scripts.offerer.file_import import UserNotCreatedException
from pcapi.scripts.offerer.file_import import create_activated_user_offerer
from pcapi.scripts.offerer.file_import import fill_offerer_from
from pcapi.scripts.offerer.file_import import fill_user_from
from pcapi.scripts.offerer.file_import import fill_user_offerer_from
from pcapi.scripts.offerer.file_import import iterate_rows_for_user_offerers
from pcapi.utils.token import random_token


class IterateRowForUserOfferersTest:
    @patch("pcapi.scripts.offerer.file_import.create_activated_user_offerer")
    def test_ignores_the_first_line_with_csv_headers(self, create_activated_user_offerer):
        # given
        create_activated_user_offerer.return_value = UserOfferer()
        csv_reader = [
            ["nom", "prénom", "email"],
            ["Mortimer", "Philip", "%s@bletchley.co.uk" % random_token()],
            ["Mortimer", "Philip", "%s@bletchley.co.uk" % random_token()],
            ["Mortimer", "Philip", "%s@bletchley.co.uk" % random_token()],
        ]

        # when
        user_offerers = iterate_rows_for_user_offerers(csv_reader)

        # then
        assert len(user_offerers) == 3

    @patch("pcapi.scripts.offerer.file_import.create_activated_user_offerer")
    def test_ignores_empty_lines(self, create_activated_user_offerer):
        # given
        create_activated_user_offerer.return_value = UserOfferer()
        csv_reader = [
            ["nom", "prénom", "email"],
            [],
            ["Mortimer", "Philip", "%s@bletchley.co.uk" % random_token()],
            [""],
            ["Mortimer", "Philip", "%s@bletchley.co.uk" % random_token()],
        ]

        # when
        user_offerers = iterate_rows_for_user_offerers(csv_reader)

        # then
        assert len(user_offerers) == 2


@pytest.mark.usefixtures("db_session")
class CreateActivatedUserOffererTest:
    def setup_method(self):
        self.csv_row = [
            "Mortimer",
            "Philip",
            "pmortimer@bletchley.co.uk",
            "29",
            "362521879",
            "29200",
            "Bletchley",
            "MyBletcheyCompany",
        ]
        self.find_user_query = Mock()
        self.find_offerer_query = Mock()
        self.find_user_offerer_query = Mock()

    def test_returns_created_user_offerer(self, app):
        # given
        blake = create_user(email="fblake@bletchley.co.uk", idx=123)
        venue_type = create_venue_type(label="Offre numérique")
        repository.save(venue_type)
        blakes_company = create_offerer(siren="362521879", name="MyBletcheyCompany", idx=234)
        self.find_user_query.side_effect = [blake]
        self.find_offerer_query.side_effect = [blakes_company]
        self.find_user_offerer_query.side_effect = [None]

        # when
        user_offerer = create_activated_user_offerer(
            self.csv_row,
            find_user=self.find_user_query,
            find_offerer=self.find_offerer_query,
            find_user_offerer=self.find_user_offerer_query,
        )

        # then
        assert user_offerer.userId == 123
        assert user_offerer.offererId == 234


@pytest.mark.usefixtures("db_session")
class FillUserOffererFromTest:
    def setup_method(self):
        self.csv_row = [
            "Mortimer",
            "Philip",
            "pmortimer@bletchley.co.uk",
            "29",
            "362521879",
            "29200",
            "Bletchley",
            "MyBletcheyCompany",
        ]

    def test_returns_a_user_offerer_built_with_user_and_offerer_relative_to_csv_row(self):
        # given
        blake = create_user(email="fblake@bletchley.co.uk", idx=123)
        blakes_company = create_offerer(siren="362521879", name="MyBletcheyCompany", idx=234)

        # when
        user_offerer = fill_user_offerer_from(UserOfferer(), blake, blakes_company)

        # then
        assert user_offerer.user == blake
        assert user_offerer.offerer == blakes_company

    def test_raise_error_when_user_relative_to_csv_not_created(self):
        # given
        blake = create_user(email="fblake@bletchley.co.uk")
        blakes_company = create_offerer(siren="362521879", name="MyBletcheyCompany", idx=234)

        # when
        with pytest.raises(UserNotCreatedException) as e:
            fill_user_offerer_from(UserOfferer(), blake, blakes_company)

    def test_raise_error_when_offerer_relative_to_csv_not_created(self):
        # given
        blake = create_user(email="fblake@bletchley.co.uk", idx=123)
        blakes_company = create_offerer(siren="362521879", name="MyBletcheyCompany")

        # when
        with pytest.raises(OffererNotCreatedException) as e:
            fill_user_offerer_from(UserOfferer(), blake, blakes_company)


@pytest.mark.usefixtures("db_session")
class FillUserFromTest:
    def setup_method(self):
        self.csv_row = [
            "Mortimer",
            "Philip",
            "pmortimer@bletchley.co.uk",
            "29",
            "362521879",
            "29200",
            "Bletchley",
            "MyBletcheyCompany",
        ]

    def test_returns_an_user_with_data_from_csv_row(self):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        assert user.lastName == "Mortimer"
        assert user.firstName == "Philip"
        assert user.publicName == "Philip Mortimer"
        assert user.email == "pmortimer@bletchley.co.uk"
        assert user.departementCode == "29"
        assert user.canBookFreeOffers == False

    @patch("pcapi.scripts.offerer.file_import.random_password")
    def test_returns_an_user_with_computed_password(self, random_password):
        # given
        random_password.return_value = "random_string"

        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        assert user.password == "random_string"

    def test_returns_only_the_first_firstname(self):
        # given
        data = list(self.csv_row)
        data[1] = "John Robert James Jack"

        # when
        user = fill_user_from(data, UserSQLEntity())

        # then
        assert user.firstName == "John"
        assert user.publicName == "John Mortimer"

    def test_sets_default_properties_on_the_user(self):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        assert user.canBookFreeOffers == False
        assert user.password

    def test_has_a_reset_password_token_and_validity_limit(self):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        thirty_days_in_the_future = datetime.utcnow() + timedelta(days=30)
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit.date() == thirty_days_in_the_future.date()

    def test_returns_the_given_user_with_modified_data_from_the_csv(self):
        # given
        existing_user = create_user(email="pmortimer@bletchley.co.uk", idx=123)

        # when
        user = fill_user_from(self.csv_row, existing_user)

        # then
        assert user.id == 123
        assert user.lastName == "Mortimer"
        assert user.firstName == "Philip"
        assert user.email == "pmortimer@bletchley.co.uk"
        assert user.departementCode == "29"
        assert user.canBookFreeOffers == False
        assert user.password != ""
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit is not None


@pytest.mark.usefixtures("db_session")
class FillOffererFromTest:
    def setup_method(self):
        self.csv_row = [
            "Mortimer",
            "Philip",
            "pmortimer@bletchley.co.uk",
            "29",
            "362521879",
            "29200",
            "Bletchley",
            "MyBletcheyCompany",
        ]

    @freeze_time("2019-10-13")
    def test_returns_an_user_with_data_from_csv_row(self):
        # when
        offerer = fill_offerer_from(self.csv_row, Offerer())

        # then
        assert offerer.siren == "362521879"
        assert offerer.name == "MyBletcheyCompany"
        assert offerer.thumbCount == 0
        assert offerer.postalCode == "29200"
        assert offerer.city == "Bletchley"
        assert offerer.dateCreated == datetime(2019, 10, 13)
