from models.mediation_sql_entity import MediationSQLEntity
from models.product import Product
from utils.object_storage import build_thumb_path

class BuildThumbPathTest:
    def test_returns_path_without_sql_entity_when_given_model_is_mediation(self):
        # given
        mediation_object = MediationSQLEntity()
        mediation_object.id = 123
        mediation_object.offerId = 567

        # when
        thumb_path = build_thumb_path(mediation_object, 0)

        #then
        assert thumb_path == 'mediations/PM'

    def test_returns_classic_path_when_given_model_is_product(self):
        # given
        product_object = Product()
        product_object.id = 123

        # when
        thumb_path = build_thumb_path(product_object, 0)

        #then
        assert thumb_path == 'products/PM'

