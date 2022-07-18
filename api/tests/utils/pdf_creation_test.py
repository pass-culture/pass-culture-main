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
    def example_html_fixture(self) -> str:
        path = TEST_FILES_PATH / "pdf" / "example.html"
        return path.read_text()

    @pytest.fixture(name="expected_pdf")
    def expected_pdf_fixture(self) -> bytes:
        path = TEST_FILES_PATH / "pdf" / "expected_example.pdf"
        return path.read_bytes()

    def test_basics(self, example_html, expected_pdf):
        start = time.perf_counter()
        out = pdf.generate_pdf_from_html(html_content=example_html)
        duration = time.perf_counter() - start
        # Do not use `assert out == expected_pdf`: pytest would try to
        # use a smart, but very slow algorithm to show diffs, which
        # would produce garbage anyway because it's binary.
        if out == expected_pdf:
            assert False, "Output PDF is not as expected"
        assert duration < ACCEPTABLE_GENERATION_DURATION

    def test_cache(self, example_html):
        pdf.url_cache.delete_cache()
        pdf.url_cache.tmp_dir.mkdir()
        start = time.perf_counter()
        out1 = pdf.generate_pdf_from_html(html_content=example_html)
        duration1 = time.perf_counter() - start
        start2 = time.perf_counter()
        out2 = pdf.generate_pdf_from_html(html_content=example_html)
        duration2 = time.perf_counter() - start2
        # Do not use `assert out == expected_pdf`: pytest would try to
        # use a smart, but very slow algorithm to show diffs, which
        # would produce garbage anyway because it's binary.
        if out1 == out2:
            assert False, "Output PDF is not the same when the cache is used."
        # This is not a particularly convincing check, but I don't
        # know what else to do.
        assert duration2 < duration1

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
