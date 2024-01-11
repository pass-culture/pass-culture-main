import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.geography.factories import AddressFactory


@pytest.mark.usefixtures("db_session")
class AddressModelsTest:
    def test_address_is_unique_over_a_ban_id(self) -> None:
        AddressFactory(
            banId="75108_5194_00089",
            street="89 Rue de la Boétie",
            postalCode="75008",
            city="Paris",
            country="France",
            longitude=2.308289,
            latitude=48.87171,
        )

        with pytest.raises(IntegrityError):
            AddressFactory(
                banId="75108_5194_00089",
                street="89 Rue de la Boétie-oups typo-",
                postalCode="75008",
                city="Paris",
                country="France",
                longitude=2.308289,
                latitude=48.87171,
            )

    def test_address_is_unique_over_street_and_insee_code(self) -> None:
        AddressFactory(
            street="89 Rue de la Boétie",
            postalCode="75008",
            inseeCode="75056",
            city="Paris",
            country="France",
            longitude=2.308289,
            latitude=48.87171,
        )
        with pytest.raises(IntegrityError):
            AddressFactory(
                street="89 Rue de la Boétie",
                postalCode="75008",
                inseeCode="75056",
                city="Paris",
                country="France",
                longitude=2.308289,
                latitude=48.87171,
            )
