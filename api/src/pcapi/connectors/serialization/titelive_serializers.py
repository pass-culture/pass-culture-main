from pcapi.routes.serialization import BaseModel


class TiteliveImage(BaseModel):
    recto: str
    verso: str | None
