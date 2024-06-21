import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.geography.factories import AddressFactory
from pcapi.core.geography.models import Address
from pcapi.models import db


class AddressModelsTest:
    @pytest.mark.usefixtures("db_session")
    def test_address_is_unique_over_street_and_insee_code(self) -> None:
        AddressFactory(
            street="89 Rue de la Boétie",
            postalCode="75008",
            inseeCode="75056",
            city="Paris",
            longitude=2.308289,
            latitude=48.87171,
        )
        with pytest.raises(IntegrityError):
            # We can't use a duplicate AddressFactory here because of `sqlalchemy_get_or_create`
            db.session.add(
                Address(
                    street="89 Rue de la Boétie",
                    postalCode="75008",
                    inseeCode="75056",
                    city="Paris",
                    longitude=2.308289,
                    latitude=48.87171,
                )
            )
            db.session.commit()

    def test_address_department_code_can_only_have_2_or_3_digits(self, db_session) -> None:
        # No departmentCode, should be fine as the field is nullable
        AddressFactory(
            street="89 Rue de la Boétie",
            postalCode="75008",
            inseeCode="75056",
            city="Paris",
            longitude=2.308289,
            latitude=48.87171,
        )
        # 2 digits, should be fine
        AddressFactory(
            street="88 Rue de la Boétie",
            postalCode="75008",
            inseeCode="75056",
            city="Paris",
            longitude=2.308288,
            latitude=48.87170,
            departmentCode="75",
        )

        # 3 digits, should be fine
        AddressFactory(
            street="Rue de Saint-Martin",
            postalCode="97150",
            inseeCode="97801",
            city="Saint-Martin",
            longitude=-63.068137,
            latitude=18.082207,
            departmentCode="978",
            timezone="America/Guadeloupe",
        )

        # 1 digit, should fail
        with pytest.raises(IntegrityError):
            AddressFactory(
                street="18 Rue Duhesme",
                postalCode="75018",
                inseeCode="75118",
                city="Paris",
                longitude=2.338562,
                latitude=48.890787,
                departmentCode="7",
            )

        db_session.rollback()

        # More than 3 digits, should fail
        with pytest.raises(IntegrityError):
            AddressFactory(
                street="18 Rue Duhesme",
                postalCode="75018",
                inseeCode="75118",
                city="Paris",
                longitude=2.338562,
                latitude=48.890787,
                departmentCode="7500",
            )
