import pytest

import pcapi.core.finance.models as finance_models
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.offers.factories import VenueFactory
import pcapi.core.users.factories as users_factories
from pcapi.models.bank_information import BankInformationStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_on_offerer(self, app):
        # given
        pro = users_factories.ProFactory()
        offerer = OffererFactory()

        venues = [
            VenueFactory(managingOfferer=offerer, businessUnit__bankAccount__status=BankInformationStatus.ACCEPTED),
            VenueFactory(managingOfferer=offerer, businessUnit__bankAccount__status=BankInformationStatus.ACCEPTED),
        ]
        VenueFactory(
            managingOfferer=offerer,
            businessUnit__bankAccount__status=BankInformationStatus.DRAFT,
        )
        VenueFactory(
            managingOfferer=offerer,
            businessUnit__bankAccount__status=BankInformationStatus.ACCEPTED,
            businessUnit__status=finance_models.BusinessUnitStatus.DELETED,
        )
        VenueFactory(
            businessUnit__bankAccount__status=BankInformationStatus.ACCEPTED,
        )
        UserOffererFactory(user=pro, offerer=offerer, validationToken=None)

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=pro.email)
        response = auth_request.get(f"/offerers/{humanize(offerer.id)}/business_units")

        # then
        assert response.status_code == 200
        assert response.json == [
            {
                "id": venue.businessUnit.id,
                "iban": venue.businessUnit.bankAccount.iban,
                "name": venue.businessUnit.name,
                "siret": venue.siret,
            }
            for venue in venues
        ]


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_doesnt_have_rights(self, app):
        # given
        pro = users_factories.ProFactory()

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=pro.email)
        response = auth_request.get(f"/offerers/{humanize(1)}/business_units")

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
