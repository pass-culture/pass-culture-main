from decimal import Decimal

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.api.institution import update_deposit_credit_ratio
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class TestUpdateDepositCreditRatio:
    def setup_method(self):
        self.ansco = educational_factories.EducationalYearFactory()
        self.institution = educational_factories.EducationalInstitutionFactory(institutionId="0470010E")
        self.deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=self.institution,
            educationalYear=self.ansco,
            creditRatio=None,
        )

    def test_replace_credit_ratio(self):
        update_deposit_credit_ratio([self.institution.institutionId], Decimal("0.5"), conflict="replace")
        db.session.refresh(self.deposit)
        assert self.deposit.creditRatio == Decimal("0.5")

    def test_keep_credit_ratio_when_none(self):
        update_deposit_credit_ratio([self.institution.institutionId], Decimal("0.7"), conflict="keep")
        db.session.refresh(self.deposit)
        assert self.deposit.creditRatio == Decimal("0.7")

    def test_keep_credit_ratio_when_already_set(self):
        self.deposit.creditRatio = Decimal("0.3")
        db.session.flush()
        update_deposit_credit_ratio([self.institution.institutionId], Decimal("0.7"), conflict="keep")
        db.session.refresh(self.deposit)

        assert self.deposit.creditRatio == Decimal("0.3")

    def test_error_conflict_raises_if_already_set(self):
        self.deposit.creditRatio = Decimal("0.2")
        db.session.flush()
        with pytest.raises(ValueError) as exc:
            update_deposit_credit_ratio([self.institution.institutionId], Decimal("0.8"), conflict="error")
        assert "Credit ratio already set for uais" in str(exc.value)

        db.session.refresh(self.deposit)
        assert self.deposit.creditRatio is None

    def test_error_if_deposit_not_found(self):
        with pytest.raises(ValueError) as exc:
            update_deposit_credit_ratio(["notfound"], Decimal("0.5"), conflict="replace")
        assert "Deposit not found for uai: notfound" in str(exc.value)

        db.session.refresh(self.deposit)
        assert self.deposit.creditRatio is None
