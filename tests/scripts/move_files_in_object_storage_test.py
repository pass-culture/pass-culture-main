from unittest.mock import MagicMock

import pytest

from utils.storage_utils import get_folder_content, build_new_filename


class MoveFilesInObjectStorageTest:

    def test_get_folder_content(self):
        # given
        container_name = 'storage-test'
        from_folder = 'events'

        connexion = MagicMock()
        connexion.get_container = MagicMock()
        connexion.get_container.return_value = [
            {'config'},
            [
                {
                    "name": 'thumbs/events/AERY'
                },
                {
                    "name": 'thumbs/mediations/A6P6'
                }
            ]
        ]

        # when
        files_info = get_folder_content(connexion, from_folder, container_name)

        # then
        assert len(files_info) == 1
        assert {"name": 'thumbs/events/AERY'} in files_info

    def test_build_new_filename(self):
        # given
        actual_filename = 'thumbs/events/AERY'
        destination_folder = 'products'

        # when
        new_filename = build_new_filename(actual_filename, destination_folder)

        # then
        assert new_filename == 'thumbs/products/AERY'
