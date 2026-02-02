import json
import pathlib
import shutil
import tempfile
import threading
import typing
import urllib.parse
from dataclasses import dataclass
from datetime import datetime

import weasyprint

from pcapi.utils import date as date_utils


PDF_AUTHOR = "Pass Culture"
url_fetcher_container = threading.local()


@dataclass
class PdfMetadata:
    title: str = ""
    description: str = ""
    author: str = PDF_AUTHOR
    created: datetime | None = None  # `now` if not given


class CachingUrlFetcher(weasyprint.URLFetcher):
    """A URL fetcher for weasyprint that caches files."""

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self.create_cache()

    def __del__(self) -> None:
        self.delete_cache()

    def create_cache(self) -> None:
        self.tmp_dir_parent = pathlib.Path(tempfile.mkdtemp())
        self.tmp_dir = self.tmp_dir_parent / "weasyprint_cache"
        self.tmp_dir.mkdir()
        # `shutil.rmtree()` may be called when the interpreter shuts
        # down. If we imported `shutil` at module-scope during
        # shutdown, it would not be available: it would be `None` and
        # accessing `shutil.rmtree` would raise an `AttributeError`
        # that would go unnoticed because exceptions are ignored
        # during shutdown.
        self.shutil_rmtree = shutil.rmtree

    def delete_cache(self) -> None:
        try:
            self.shutil_rmtree(self.tmp_dir_parent)
        except Exception:
            pass

    def fetch(self, url: str, headers: dict | None = None) -> weasyprint.urls.URLFetcherResponse:
        base_cache_key = urllib.parse.quote_plus(url)
        content_cache_key = base_cache_key + ".content"
        headers_cache_key = base_cache_key + ".headers"
        content_path = self.tmp_dir / content_cache_key
        headers_path = self.tmp_dir / headers_cache_key
        if content_path.exists():
            return weasyprint.urls.URLFetcherResponse(
                url,
                body=content_path.read_bytes(),
                headers=json.loads(headers_path.read_text()),
            )

        result = super().fetch(url, headers)

        content = result.read()
        with content_path.open("bx") as fp:
            fp.write(content)
        with headers_path.open("tx", encoding="utf-8") as fp:
            fp.write(json.dumps(dict(result.headers)))
        if result._file_obj.seekable():
            result._file_obj.seek(0)
            return result
        # Gzip content is not seekable, can't be read twice
        return weasyprint.urls.URLFetcherResponse(url, body=content, headers=result.headers, status=result.status)


def _get_url_fetcher() -> CachingUrlFetcher:
    if not hasattr(url_fetcher_container, "fetcher"):
        url_fetcher_container.fetcher = CachingUrlFetcher()
    return url_fetcher_container.fetcher


def generate_pdf_from_html(html_content: str, metadata: PdfMetadata | None = None) -> bytes:
    fetcher = _get_url_fetcher()
    document = weasyprint.HTML(string=html_content, url_fetcher=fetcher).render()
    metadata = metadata or PdfMetadata()
    # a W3C date, as expected by Weasyprint
    document.metadata.created = (metadata.created or date_utils.get_naive_utc_now()).strftime("%Y-%m-%dT%H:%M:%SZ")
    document.metadata.modified = document.metadata.created
    document.metadata.authors = [metadata.author]
    document.metadata.title = metadata.title
    document.metadata.description = metadata.description
    return document.write_pdf()
