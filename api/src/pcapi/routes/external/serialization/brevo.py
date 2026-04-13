from pcapi.routes.serialization import HttpBodyModel


class RecommendedOffer(HttpBodyModel):
    image: str | None = None
    name: str
    url: str


class BrevoOffersResponse(HttpBodyModel):
    # For integration with Brevo data feeds,
    # the response root must not be a list
    offers: list[RecommendedOffer]
