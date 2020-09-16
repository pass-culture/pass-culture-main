from connectors.api_local_provider import ApiLocalProvider


class ApiHttpLibrairesStocks(ApiLocalProvider):
    pass


class ApiHttpFnacStocks(ApiLocalProvider):
    def get_stocks_from_local_provider_api(self, siret: str, last_processed_isbn: str = '', modified_since: str = '',
                                           limit: int = 1000) -> Dict:
        api_url = self._build_local_provider_url(siret)
        params = self._build_local_provider_params(last_processed_isbn, modified_since, limit)

        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            raise ApiLocalProviderException(
                f'Error {response.status_code} when getting {self.name} stocks for SIRET: {siret}')

        return response.json()