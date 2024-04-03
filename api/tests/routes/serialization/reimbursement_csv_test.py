import datetime

from pcapi.routes.serialization.reimbursement_csv_serialize import _get_validation_period
from pcapi.routes.serialization.reimbursement_csv_serialize import _legacy_get_validation_period


in_two_days = datetime.date.today() + datetime.timedelta(days=2)
reimbursement_period = (datetime.date(2022, 1, 1), in_two_days)


def test_get_validation_period() -> None:
    assert (
        _get_validation_period(cutoff=datetime.datetime(2022, 1, 16))
        == "Validées et remboursables sur janvier : 1ère quinzaine"
    )
    assert (
        _get_validation_period(cutoff=datetime.datetime(2022, 2, 1))
        == "Validées et remboursables sur janvier : 2nde quinzaine"
    )


def test_legacy_get_validation_period() -> None:
    assert (
        _legacy_get_validation_period("pass Culture Pro - remboursement 1ère quinzaine 06-2019")
        == "Validées et remboursables sur mai : 2nde quinzaine"
    )
    assert (
        _legacy_get_validation_period("pass Culture Pro - remboursement 2ème quinzaine 06-2019")
        == "Validées et remboursables sur juin : 1ère quinzaine"
    )
