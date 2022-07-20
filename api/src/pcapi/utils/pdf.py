from dataclasses import dataclass
from datetime import datetime
import json
import pathlib
import shutil
import tempfile
import urllib.parse

import weasyprint


PDF_AUTHOR = "Pass Culture"


@dataclass
class PdfMetadata:
    title: str = ""
    description: str = ""
    author: str = PDF_AUTHOR
    created: datetime | None = None  # `now` if not given


class CachingUrlFetcher:
    """A URL fetcher for weasyprint that caches files."""

    def __init__(self) -> None:
        self.tmp_dir = pathlib.Path(tempfile.mkdtemp()) / "weasyprint_cache"
        self.tmp_dir.mkdir()

    def __del__(self) -> None:
        self.delete_cache()

    def delete_cache(self) -> None:
        try:
            shutil.rmtree(self.tmp_dir)
        except Exception:  # pylint: disable=broad-except
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


url_cache = CachingUrlFetcher()


def generate_pdf_from_html(html_content: str, metadata: PdfMetadata = None) -> bytes:
    document = weasyprint.HTML(string=html_content, url_fetcher=url_cache.fetch_url).render()
    metadata = metadata or PdfMetadata()
    # a W3C date, as expected by Weasyprint
    document.metadata.created = (metadata.created or datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")
    document.metadata.modified = document.metadata.created
    document.metadata.authors = [metadata.author]
    document.metadata.title = metadata.title
    document.metadata.description = metadata.description
    return document.write_pdf()
