from pcapi.core.offerers.models import VenueLabel
from pcapi.routes.serialization.venue_labels_serialize import VenueLabelResponseModel


class SerializeVenueLabelsTest:
    def should_return_dict_with_expected_information(self):
        # Given
        venue_label = VenueLabel(id=1, label="Maison des illustres")

        # When
        serialized_label_response = VenueLabelResponseModel.from_orm(venue_label)

        # Then
        assert serialized_label_response == {"id": venue_label.id, "label": venue_label.label}
