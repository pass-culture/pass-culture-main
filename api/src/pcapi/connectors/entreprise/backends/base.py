import datetime

from pcapi.connectors.entreprise import models
from pcapi.utils import module_loading


def get_backend(module_path: str | None) -> "BaseBackend":
    assert module_path is not None
    backend_class = module_loading.import_string(module_path)
    return backend_class()


class BaseBackend:
    def get_siren_open_data(self, siren: str, with_address: bool = True) -> models.SirenInfo:
        raise NotImplementedError()

    def get_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
        raise NotImplementedError()

    def get_siret_open_data(self, siret: str) -> models.SiretInfo:
        raise NotImplementedError()

    def get_siret(self, siret: str, raise_if_non_public: bool = False) -> models.SiretInfo:
        raise NotImplementedError()

    def get_rcs(self, siren: str) -> models.RCSInfo:
        raise NotImplementedError()

    def get_urssaf(self, siren: str) -> models.UrssafInfo:
        raise NotImplementedError()

    def get_dgfip(self, siren: str) -> models.DgfipInfo:
        raise NotImplementedError()

    def get_siren_closed_at_date(self, date_closed: datetime.date) -> list[str]:
        raise NotImplementedError()
