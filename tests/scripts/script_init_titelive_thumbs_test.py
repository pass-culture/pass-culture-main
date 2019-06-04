import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call, ANY

from models import PcObject
from scripts.init_titelive.import_thumbs import import_init_titelive_thumbs
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_product_with_Thing_type
from utils.human_ids import humanize


class InitTiteliveThumbsTest:

    @clean_database
    @patch('scripts.init_titelive.import_thumbs.compute_dominant_color')
    def test_register_image_from_object_storage_second_version(self,
                                                               compute_dominant_color,
                                                               app):
        # given
        offerer = create_offerer(siren='987654321')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        product_1 = create_product_with_Thing_type(id_at_providers='3663608844000',
                                                   thumb_count=0)

        PcObject.save(product_1)

        filename_to_save_1 = 'thumbs/titelive/3663608844000_1_v.jpg'
        filename_to_save_2 = 'thumbs/titelive/3663608844000_1_75.jpg'

        connexion = MagicMock()
        connexion.get_container = MagicMock()
        connexion.get_container.side_effect = [
            [
                {'config'},
                [
                    {
                        "name": filename_to_save_1
                    },
                    {
                        "name": filename_to_save_2
                    }
                ]
            ],
            [
                {},
                []
            ]
        ]

        test_jpeg_image_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                               / 'script_init_titelive_thumbs_test_image.jpg'
        test_jpeg_image = open(test_jpeg_image_path, "rb").read()
        image_content = test_jpeg_image

        connexion.get_object = MagicMock()
        connexion.get_object.return_value = ['init_thumbs_test_image.jpg', image_content]

        connexion.put_object = MagicMock()
        connexion.delete_object = MagicMock()

        compute_dominant_color.return_value = b'\x00\x00\x00'

        container_name = "storage-pc-testing"
        titelive_thumb_identifier = 'titelive/'

        # when
        import_init_titelive_thumbs(connexion, container_name, titelive_thumb_identifier)

        # then
        assert product_1.thumbCount == 2
        assert product_1.firstThumbDominantColor == b'\x00\x00\x00'

        assert connexion.get_object.call_count == 2
        assert connexion.get_object.call_args_list[0] == call(container_name, filename_to_save_1)
        assert connexion.get_object.call_args_list[1] == call(container_name, filename_to_save_2)

        assert connexion.put_object.call_args_list[0] == call(container_name,
                                                              'thumbs/products/' + humanize(product_1.id),
                                                              content_type='image/jpeg', contents=ANY)
        assert connexion.put_object.call_args_list[1] == call(container_name,
                                                              'thumbs/products/' + humanize(product_1.id) + '_1',
                                                              content_type='image/jpeg', contents=ANY)

        assert connexion.delete_object.call_args_list[0] == call(container_name, filename_to_save_1)
        assert connexion.delete_object.call_args_list[1] == call(container_name, filename_to_save_2)
