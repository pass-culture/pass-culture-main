from pydantic import BaseModel


class TiteliveImage(BaseModel):
    recto: str
    verso: str | None = None
