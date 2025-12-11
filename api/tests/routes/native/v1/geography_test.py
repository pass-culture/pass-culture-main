from pcapi.core.users import factories as users_factories
from pcapi.utils import countries as countries_utils


class CountriesTest:
    def test_get_countries(self, client):
        user = users_factories.BeneficiaryFactory.create()

        response = client.with_token(user).get("/native/v1/countries")

        assert response.status_code == 200
        assert response.json["countries"][0] == {"cog": int(countries_utils.FRANCE_INSEE_CODE), "libcog": "France"}
