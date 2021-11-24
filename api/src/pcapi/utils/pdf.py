from dataclasses import dataclass
from datetime import datetime

from weasyprint import HTML


PDF_AUTHOR = "Pass Culture"


@dataclass
class PdfMetadata:
    title: str = ""
    description: str = ""
    author: str = PDF_AUTHOR


def generate_pdf_from_html(html_content: str, metadata: PdfMetadata = None) -> bytes:
    document = HTML(string=html_content).render()
    # a W3C date, as expected by Weasyprint
    metadata = metadata or PdfMetadata()
    document.metadata.created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    document.metadata.modified = document.metadata.created
    document.metadata.authors = [metadata.author]
    document.metadata.title = metadata.title
    document.metadata.description = metadata.description
    return document.write_pdf()
