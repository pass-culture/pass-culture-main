from models import Provider, PcObject
from models.db import db
from repository.provider_queries import get_enabled_providers_for_pro
from tests.conftest import clean_database


class GetEnabledProvidersForProTest:
    @clean_database
    def test_get_enabled_providers_for_pro(self, app):
        # given
        provider1 = Provider()
        provider1.name = 'Open Agenda'
        provider1.localClass = 'OpenAgenda'
        provider1.isActive = False
        provider1.enabledForPro = False

        provider2 = Provider()
        provider2.name = 'Tite Live'
        provider2.localClass = 'TiteLive'
        provider2.isActive = True
        provider2.enabledForPro = True
        PcObject.save(provider1, provider2)

        # when
        enabled_providers = get_enabled_providers_for_pro()

        # then
        assert enabled_providers == [provider2]

        # clean
        db.session.delete(provider1)
        db.session.delete(provider2)
        db.session.commit()
