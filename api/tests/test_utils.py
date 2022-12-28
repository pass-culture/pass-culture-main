import datetime
import enum
import operator
import uuid

from pcapi.core.offerers import factories as offerers_factories


def json_default(data):
    conversions = {
        enum.Enum: operator.attrgetter("value"),
        datetime.datetime: str,
        uuid.UUID: str,
    }
    for type_, func in conversions.items():
        if isinstance(data, type_):
            return func(data)

    return data


def gen_offerer_tags():
    tags = [offerers_factories.OffererTagFactory(label=label) for label in ("Collectivité", "Établissement public")]
    tags.append(offerers_factories.OffererTagFactory(name="partenaire-national", label="Partenaire national"))
    return tags
