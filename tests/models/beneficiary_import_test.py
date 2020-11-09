from datetime import datetime
from datetime import timedelta

from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus


class SetStatusTest:
    def test_appends_a_status_to_a_new_beneficiary_import(self):
        # given
        one_second = timedelta(seconds=1)
        now = datetime.utcnow()
        beneficiary_import = BeneficiaryImport()

        # when
        beneficiary_import.setStatus(ImportStatus.CREATED)

        # then
        assert len(beneficiary_import.statuses) == 1
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert beneficiary_import.detail is None
        assert now - one_second < beneficiary_import.statuses[0].date < now + one_second

    def test_appends_a_status_to_a_beneficiary_import_with_existing_status(self):
        # given
        one_second = timedelta(seconds=1)
        now = datetime.utcnow()
        beneficiary_import = BeneficiaryImport()
        payment_status = BeneficiaryImportStatus()
        payment_status.status = ImportStatus.DUPLICATE
        payment_status.date = datetime.utcnow()
        beneficiary_import.statuses = [payment_status]

        # when
        beneficiary_import.setStatus(ImportStatus.REJECTED)

        # then
        assert len(beneficiary_import.statuses) == 2
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED
        assert beneficiary_import.detail is None
        assert now - one_second < beneficiary_import.statuses[1].date < now + one_second
