import datetime
import os
import pathlib
import time
from unittest import mock

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

    def test_basics(self, example_html, expected_pdf, css_font_http_request_mock):
        start = time.perf_counter()
        out = pdf.generate_pdf_from_html(html_content=example_html)
        duration = time.perf_counter() - start
        # Do not use `assert out == expected_pdf`: pytest would try to
        # use a smart, but very slow algorithm to show diffs, which
        # would produce garbage anyway because it's binary.
        if out == expected_pdf:
            assert False, "Output PDF is not as expected"
        assert duration < ACCEPTABLE_GENERATION_DURATION

    # Setting `SOURCE_DATE_EPOCH` is necessary for fonttools (and thus
    # weasyprint) to be stable across time. Otherwise, if two
    # consecutive renderings are done with a one-second interval, the
    # output is different.
    @mock.patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "0"}, clear=True)
    def test_cache(self, example_html, css_font_http_request_mock):
        # Force recreation of the cache.
        fetcher = pdf._get_url_fetcher()
        fetcher.delete_cache()
        fetcher.create_cache()
        metadata = pdf.PdfMetadata(created=datetime.datetime.utcnow())
        out1 = pdf.generate_pdf_from_html(example_html, metadata)
        out2 = pdf.generate_pdf_from_html(example_html, metadata)
        # Do not use `assert out == expected_pdf`: pytest would try to
        # use a smart, but very slow algorithm to show diffs, which
        # would produce garbage anyway because it's binary.
        if out1 != out2:
            assert False, "Output PDF is not the same when the cache is used."
        # We have tried to check that the second run was quicker than
        # the first run, but it often failed on CI, even though
        # debugging statements showed that the cache was used (and
        # thus that the second run should be faster).

    def test_metadata(self, example_html, css_font_http_request_mock):
        date_string = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S") + "Z"
        metadata = pdf.PdfMetadata(
            author="Pass Culture Dev Team",
            title="Le dispositif pass Culture",
            description="Des explications issues du site",
        )
        pdf_file = pdf.generate_pdf_from_html(html_content=example_html, metadata=metadata)
        assert "/Author (Pass Culture Dev Team)".encode() in pdf_file
        assert "/Title (Le dispositif pass Culture)".encode() in pdf_file
        assert f"/CreationDate ({date_string})".encode() in pdf_file
        assert f"/ModDate ({date_string})".encode() in pdf_file
