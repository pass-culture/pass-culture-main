from pcapi.core.offerers.models import VenueLabel
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelResponseModel


class SerializeVenueLabelsTest:
    def should_return_dict_with_expected_information(self):
        venue_label = VenueLabel(id=1, label="Maison des illustres")

        serialized_label_response = VenueLabelResponseModel.model_validate(venue_label)

        assert serialized_label_response.model_dump() == {"id": venue_label.id, "label": venue_label.label}
