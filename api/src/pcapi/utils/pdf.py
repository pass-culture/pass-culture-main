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


class CachingUrlFetcher:
    """A URL fetcher for weasyprint that caches files."""

    def __init__(self) -> None:
        self.tmp_dir = pathlib.Path(tempfile.mkdtemp()) / "weasyprint_cache"
        self.tmp_dir.mkdir()

    def __del__(self) -> None:
        self.clean_cache()

    def clean_cache(self) -> None:
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
        content_path.write_bytes(result["string"])  # despite the name, it's bytes
        metadata = {key: value for key, value in result.items() if key != "string"}
        metadata_path.write_text(json.dumps(metadata))
        return result


url_cache = CachingUrlFetcher()


def generate_pdf_from_html(html_content: str, metadata: PdfMetadata = None) -> bytes:
    document = weasyprint.HTML(string=html_content, url_fetcher=url_cache.fetch_url).render()
    # a W3C date, as expected by Weasyprint
    metadata = metadata or PdfMetadata()
    document.metadata.created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    document.metadata.modified = document.metadata.created
    document.metadata.authors = [metadata.author]
    document.metadata.title = metadata.title
    document.metadata.description = metadata.description
    return document.write_pdf()
