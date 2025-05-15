import json
import pathlib
import shutil
import tempfile
import threading
import urllib.parse
from dataclasses import dataclass
from datetime import datetime

import weasyprint


PDF_AUTHOR = "Pass Culture"
url_fetcher_container = threading.local()


@dataclass
class PdfMetadata:
    title: str = ""
    description: str = ""
    author: str = PDF_AUTHOR
    created: datetime | None = None  # `now` if not given


class CachingUrlFetcher:
    """A URL fetcher for weasyprint that caches files."""

    def __init__(self) -> None:
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

    def fetch_url(self, url: str) -> dict:
        content_cache_key = urllib.parse.quote_plus(url)
        metadata_cache_key = content_cache_key + ".metadata"
        content_path = self.tmp_dir / content_cache_key
        metadata_path = self.tmp_dir / metadata_cache_key
        if content_path.exists():
            result = {
                "string": content_path.read_bytes(),
            }
            return result | json.loads(metadata_path.read_text())

        result = weasyprint.default_url_fetcher(url)
        if "file_obj" in result:
            # File objects cannot be serialized, we serialize their
            # content instead.
            result["string"] = result.pop("file_obj").read()  # type: ignore[attr-defined]
        with content_path.open("bx") as fp:
            fp.write(result["string"])  # despite the name, it's bytes
        metadata = {key: value for key, value in result.items() if key != "string"}
        with metadata_path.open("tx", encoding="utf-8") as fp:
            fp.write(json.dumps(metadata))
        return result


def _get_url_fetcher() -> CachingUrlFetcher:
    if not hasattr(url_fetcher_container, "fetcher"):
        url_fetcher_container.fetcher = CachingUrlFetcher()
    return url_fetcher_container.fetcher


def generate_pdf_from_html(html_content: str, metadata: PdfMetadata | None = None) -> bytes:
    fetcher = _get_url_fetcher()
    document = weasyprint.HTML(string=html_content, url_fetcher=fetcher.fetch_url).render()
    metadata = metadata or PdfMetadata()
    # a W3C date, as expected by Weasyprint
    document.metadata.created = (metadata.created or datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")
    document.metadata.modified = document.metadata.created
    document.metadata.authors = [metadata.author]
    document.metadata.title = metadata.title
    document.metadata.description = metadata.description
    return document.write_pdf()
