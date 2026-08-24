import pytest

from pcapi.core.geography import factories as geography_factories
from pcapi.models import api_errors
from pcapi.routes.public import utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetAddressOrRaise404Test:
    def test_should_return_the_address_matching_the_id(self):
        address = geography_factories.AddressFactory()
        geography_factories.AddressFactory()

        assert utils.get_address_or_raise_404(address.id) == address

    def test_should_raise_a_404_when_no_address_matches_the_id(self):
        address = geography_factories.AddressFactory()
        unknown_address_id = address.id + 1000

        with pytest.raises(api_errors.ResourceNotFoundError) as error:
            utils.get_address_or_raise_404(unknown_address_id)

        assert error.value.errors == {
            "location.AddressLocation.addressId": [f"There is no address with id {unknown_address_id}"]
        }
        assert error.value.status_code == 404
