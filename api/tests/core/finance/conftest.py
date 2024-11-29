import pytest

from pcapi.core.finance.backend import dummy as dummy_backend


@pytest.fixture(scope="function")
def clean_dummy_backend_data():
    yield
    dummy_backend.clear_invoices()
    dummy_backend.clear_bank_accounts()
