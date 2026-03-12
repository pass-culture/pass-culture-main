from datetime import date
from pathlib import Path

import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.scripts.upload_reimbursement_csv import main


pytestmark = pytest.mark.usefixtures("db_session")


class FileNameTest:
    @pytest.mark.parametrize(
        "inputs",
        [
            pytest.param((1, []), id="(1, [])"),
            pytest.param((1, None), id="(1, None)"),
            pytest.param((None, [1]), id="(None, [1])"),
        ],
    )
    def test_missing_inputs_raises_an_exception(self, inputs):
        with pytest.raises(main.MissingContext):
            main.file_name(date.today(), *inputs)

    def test_builds_expected_with_one_invoice(self):
        today = date(2026, 3, 1)
        expected = "invoices_offerer-1_2026-3-1_ID.csv"
        assert main.file_name(today, 1, ["ID"]) == expected

    def test_builds_expected_with_many_invoices(self):
        today = date(2026, 3, 1)
        expected = "invoices_offerer-1_2026-3-1_ID1_ID2.csv"
        assert main.file_name(today, 1, ["ID1", "ID2"]) == expected


class FilePathTest:
    def test_output_directory_env_variable_is_mandatory(self):
        with pytest.raises(main.MissingContext):
            main.file_path("file.name")

    @pytest.mark.parametrize("dir", ["/base/dir", "/base/dir/", "/"])
    def test_file_path_builds_as_expected(self, monkeypatch, dir):
        with monkeypatch.context() as m:
            m.setenv("OUTPUT_DIRECTORY", dir)
            # checking that no error is raised is enough for this test
            # more detailed test should be run inside a more end to end
            # one.
            main.file_path("file.name") is not None


class GenerateCsvTest:
    @pytest.mark.parametrize("invoices", [pytest.param([], id="[]"), pytest.param(None, id="None")])
    def test_missing_invoices_raises_an_exception(self, invoices):
        with pytest.raises(main.MissingContext):
            main.generate_csv(invoices)

    def test_returns_empty_content_if_nothing_to_build(self):
        content = main.generate_csv(["nothing"])
        assert len(content.splitlines()) == 1  # header only

    def test_build_csv_from_invoices(self):
        bank_account = finance_factories.BankAccountFactory()
        invoices = finance_factories.InvoiceFactory.create_batch(3, bankAccount=bank_account)
        cashflow = finance_factories.CashflowFactory(bankAccount=bank_account, invoices=invoices)
        finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, cashflows=[cashflow])

        content = main.generate_csv([invoice.reference for invoice in invoices])

        # ignore header row
        rows = content.splitlines()[1:]
        assert len(rows) == len(invoices)

        for row in rows:
            assert cashflow.batch.label in row

        for invoice in invoices:
            assert any([invoice.reference in row for row in rows])


class RunTest:
    def test_generate_and_upload_as_expected(self, tmp_path, monkeypatch):
        bank_account = finance_factories.BankAccountFactory()
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)
        cashflow = finance_factories.CashflowFactory(bankAccount=bank_account, invoices=[invoice])
        finance_factories.PricingFactory(status=finance_models.PricingStatus.INVOICED, cashflows=[cashflow])

        with monkeypatch.context() as m:
            m.setenv("OUTPUT_DIRECTORY", tmp_path)

            day = date(2026, 3, 1)
            main.run(day, 1, [invoice.reference])

            assert len(list(tmp_path.iterdir())) == 1

            name = Path(f"invoices_offerer-1_2026-3-1_{invoice.reference}.csv")
            with open(Path(tmp_path) / Path(name)) as f:
                content = f.read()

                assert len(content.splitlines()) == 2
                assert invoice.reference in content
