from models import Feature
from models.feature import FeatureToggle
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_user
from utils.human_ids import humanize

RECOMMENDATION_URL_V3 = '/recommendations/v3'


class Put:
    class Returns403:
        @clean_database
        def when_feature_is_not_active(self, app):
            # Given
            user = create_user(can_book_free_offers=True, departement_code='973', is_admin=False)
            feature = Feature.query.filter_by(name=FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION).first()
            feature.isActive = False
            repository.save(feature, user)
            reads = [
                {"id": humanize(1), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(2), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(3), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            response = auth_request.put(RECOMMENDATION_URL_V3,
                                        json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 403

    class Returns200:
        @clean_database
        def when_feature_is_active(self, app):
            # Given
            user = create_user(can_book_free_offers=True, departement_code='973', is_admin=False)
            feature = Feature.query.filter_by(name=FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION).first()
            feature.isActive = True
            repository.save(feature, user)
            reads = [
                {"id": humanize(1), "dateRead": "2018-12-17T15:59:11.689000Z"},
                {"id": humanize(2), "dateRead": "2018-12-17T15:59:15.689000Z"},
                {"id": humanize(3), "dateRead": "2018-12-17T15:59:21.689000Z"},
            ]
            data = {'readRecommendations': reads}
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # When
            response = auth_request.put(RECOMMENDATION_URL_V3,
                                        json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 200