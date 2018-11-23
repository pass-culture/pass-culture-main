import pytest

from models import PcObject
from recommendations_engine import create_recommendations_for_discovery
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import create_user, create_offerer, create_venue, create_thing_offer, create_stock_from_offer, \
    create_mediation


@clean_database
@pytest.mark.standalone
def test_create_recommendations_for_discovery_does_not_put_mediation_ids_of_inactive_mediations(app):
    # Given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer1 = create_thing_offer(venue, thumb_count=0)
    stock1 = create_stock_from_offer(offer1, price=0)
    mediation1 = create_mediation(offer1, is_active=False)
    offer2 = create_thing_offer(venue, thumb_count=0)
    stock2 = create_stock_from_offer(offer2, price=0)
    mediation2 = create_mediation(offer2, is_active=False)
    mediation3 = create_mediation(offer2, is_active=True)
    PcObject.check_and_save(user, stock1, mediation1, stock2, mediation2, mediation3)

    # When
    recommendations = create_recommendations_for_discovery(user=user)

    # Then
    mediations = list(map(lambda x: x.mediationId, recommendations))
    assert len(recommendations) == 2
    assert mediation3.id in mediations
    assert humanize(mediation2.id) not in mediations
    assert humanize(mediation1.id) not in mediations
