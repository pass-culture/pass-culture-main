from io import BytesIO

from pypdf import PdfReader
import pytest

from pcapi.core.finance import factories
from pcapi.core.users import factories as users_factories

from tests.utils.pdf_creation_test import TEST_FILES_PATH


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="invoice_1_example_pdf")  # 1 page pdf
def invoice_1_example_pdf_fixture() -> bytes:
    path = TEST_FILES_PATH / "pdf" / "invoice_1_example.pdf"
    return path.read_bytes()


@pytest.fixture(name="invoice_2_example_pdf")  # 2 pages pdf
def invoice_2_example_pdf_fixture() -> bytes:
    path = TEST_FILES_PATH / "pdf" / "invoice_2_example.pdf"
    return path.read_bytes()


def test_get_combined_invoices_pdf(client, requests_mock, invoice_1_example_pdf, invoice_2_example_pdf):
    invoice_1 = factories.InvoiceFactory(reference="F240000187")
    invoice_2 = factories.InvoiceFactory(reference="F240000189")

    requests_mock.get(invoice_1.url, content=invoice_1_example_pdf)
    requests_mock.get(invoice_2.url, content=invoice_2_example_pdf)

    pro = users_factories.ProFactory()
    client = client.with_session_auth(pro.email)

    response = client.get("/finance/combined-invoices?invoiceReferences=F240000189&invoiceReferences=F240000187")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=justificatifs_de_remboursement.pdf"
    assert PdfReader(BytesIO(response.data)).get_num_pages() == 3


def test_get_one_invoice_pdf(client, requests_mock, invoice_1_example_pdf):
    invoice = factories.InvoiceFactory(reference="F240000187")

    requests_mock.get(invoice.url, content=invoice_1_example_pdf)

    pro = users_factories.ProFactory()
    client = client.with_session_auth(pro.email)

    response = client.get("/finance/combined-invoices?invoiceReferences=F240000187")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=justificatifs_de_remboursement.pdf"
    assert PdfReader(BytesIO(response.data)).get_num_pages() == 1


def test_get_combined_invoices_pdf_404(client):
    pro = users_factories.ProFactory()
    client = client.with_session_auth(pro.email)

    response = client.get("/finance/combined-invoices?invoiceReferences=F240000000&invoiceReferences=F240000001")

    assert response.status_code == 404
    assert response.json == {"invoice": "Invoice not found"}


def test_get_combined_invoices_pdf_user_not_loged_in(client):
    response = client.get("/finance/combined-invoices?invoiceReferences=F240000000")

    assert response.status_code == 401


def test_get_combined_invoices_pdf_no_invoice_references(client):
    pro = users_factories.ProFactory()
    client = client.with_session_auth(pro.email)

    response = client.get("/finance/combined-invoices")

    assert response.status_code == 400
    assert response.json == {"invoiceReferences": ["Ce champ est obligatoire"]}
