""" local providers test """

from local_providers import InitTiteLiveThingDescriptions
from models import PcObject
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type


class InitTiteLiveThingDescriptionsTest:

    @clean_database
    def test_does_not_update_thing_when_unknonw_id_at_providers_in_given_zip_file(self, app):
        # given
        filename = 'tests/local_providers/Resume-full_01012019.zip'

        thing_1 = create_product_with_thing_type(id_at_providers='1234567029006')
        init_titelive_thing_descriptions = InitTiteLiveThingDescriptions(filename)
        init_titelive_thing_descriptions.dbObject.isActive = True
        PcObject.save(thing_1, init_titelive_thing_descriptions.dbObject)

        # when
        init_titelive_thing_descriptions.updateObjects()

        # then
        assert init_titelive_thing_descriptions.checkedObjects == 0
        assert init_titelive_thing_descriptions.updatedObjects == 0

    @clean_database
    def test_only_update_thing_when_known_id_at_providers_in_given_zip_file(self, app):
        # given
        filename = 'tests/local_providers/Resume-full_01012019.zip'

        thing_1 = create_product_with_thing_type(id_at_providers='1234567029006')
        thing_2 = create_product_with_thing_type(id_at_providers='9782711029006')
        thing_3 = create_product_with_thing_type(id_at_providers='3760107140005')
        init_titelive_thing_descriptions = InitTiteLiveThingDescriptions(filename)
        init_titelive_thing_descriptions.dbObject.isActive = True
        PcObject.save(thing_1, thing_2, thing_3, init_titelive_thing_descriptions.dbObject)

        # when
        init_titelive_thing_descriptions.updateObjects()

        # then
        assert init_titelive_thing_descriptions.checkedObjects == 2
        assert init_titelive_thing_descriptions.updatedObjects == 2
