import pathlib
import time

from freezegun import freeze_time
import pytest

from pcapi.utils import pdf

import tests


TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"
ACCEPTABLE_GENERATION_DURATION = 2  # seconds. The CI might be quite slow.


class GeneratePdfFromHtmlTest:
    @pytest.fixture(name="example_html")
    def example_html_fixture(self):
        with open(TEST_FILES_PATH / "pdf" / "example.html", "r", encoding="utf-8") as f:
            example_html = f.read()
        return example_html

    def test_performance(self, example_html):
        start = time.perf_counter()

        pdf.generate_pdf_from_html(html_content=example_html)

        duration = time.perf_counter() - start
        assert duration < ACCEPTABLE_GENERATION_DURATION

    @freeze_time("2021-07-30 17:25:00")
    def test_metadata(self, example_html):
        metadata = pdf.PdfMetadata(
            author="Pass Culture Dev Team",
            title="Le dispositif pass Culture",
            description="Des explications issues du site",
        )
        pdf_file = pdf.generate_pdf_from_html(html_content=example_html, metadata=metadata)
        assert b"/Author (Pass Culture Dev Team)" in pdf_file
        assert b"/Title (Le dispositif pass Culture)" in pdf_file
        assert b"/CreationDate (20210730172500Z)" in pdf_file
        assert b"/ModDate (20210730172500Z)" in pdf_file
