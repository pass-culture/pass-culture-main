from typing import Dict

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI


class TiteliveProviderAPI(ProviderAPI):
    def __init__(self, api_url: str, name: str):
        super().__init__(api_url, name)

    def _build_local_provider_params(self, last_processed_isbn: str, modified_since: str, limit: int) -> Dict:
        params = {"limit": str(limit)}

        if last_processed_isbn:
            params["after"] = last_processed_isbn

        if modified_since:
            params["modifiedSince"] = modified_since
        else:
            params["inStock"] = "1"

        return params
