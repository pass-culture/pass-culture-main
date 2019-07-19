import pytest
import os
import shutil

from models import PcObject
from scripts.init_titelive.local_format_thumbs import get_files_from_folder, write_file_to_directory, \
    get_all_sub_directories, extract_book_ean13, format_all_thumbs
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type
from utils.human_ids import humanize


@pytest.mark.standalone
class LocalFormatThumbsTest():
    test_directory = '/tmp/test_directory'

    @pytest.fixture(autouse=True)
    def clean_files_and_directory(self):
        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

    @clean_database
    def test_format_all_thumbs(self, app):
        # given
        product = create_product_with_thing_type(id_at_providers='0002730757438')

        source_directory = self.test_directory + "/images"
        source_subdirectory = self.test_directory + "/images/001"
        destination_directory = self.test_directory + "/products"

        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)
            os.makedirs(source_directory)
            os.makedirs(source_subdirectory)
            os.makedirs(destination_directory)

        image_content = open('static/images/default_thumb.png', 'rb')

        file = open(source_subdirectory + "/0002730757438_1_75.jpg", "wb")
        file.write(image_content.read())
        file.close()

        file = open(source_subdirectory + "/0002730757438_4_75.jpg", "wb")
        file.write(image_content.read())
        file.close()

        PcObject.save(product)

        expected_thumb_id = humanize(product.id)

        # when
        format_all_thumbs(source_directory, destination_directory)

        # then
        expected_filename_1 = "%s/%s" % (destination_directory, expected_thumb_id)
        expected_filename_2 = "%s/%s" % (destination_directory, expected_thumb_id + "_1")
        assert os.path.exists(expected_filename_1)
        assert os.path.exists(expected_filename_2)

    def test_get_files_from_folder_list_0_files_in_empty_directory(self):
        # given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        # when
        files = get_files_from_folder(self.test_directory)

        # then
        assert len(files) == 0

    def test_get_files_from_folder_list_2_files_in_created_directory(self):
        # given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        file = open(self.test_directory + "/test_1_75.jpg", "w")
        file.write("Test 1")
        file.close()

        file = open(self.test_directory + "/test_2_75.jpg", "w")
        file.write("Test 2")
        file.close()

        # when
        files = get_files_from_folder(self.test_directory)

        # then
        assert len(files) == 2

    def test_get_files_from_folder_list_only_1_files_with_correct_extension_directory(self):
        # given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        file = open(self.test_directory + "/test_1_75.jpg", "w")
        file.write("Test 1")
        file.close()

        file = open(self.test_directory + "/test_1_v.jpg", "w")
        file.write("Test 2")
        file.close()

        # when
        files = get_files_from_folder(self.test_directory)

        # then
        assert files[0] == self.test_directory + "/test_1_75.jpg"

    def test_write_files_to_directory_write_content_to_destination_folder(self):
        # Given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        file_content = open('static/images/default_thumb.png', 'rb')
        filename = 'image_id'

        # When
        write_file_to_directory(self.test_directory,
                                filename,
                                file_content)

        # Then
        assert os.path.exists("%s/%s" % (self.test_directory, filename))

    def test_write_files_to_directory_increment_filename_when_already_one_file_with_same_ean13(self):
        # Given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        filename = 'image_id'
        file_content = open('static/images/default_thumb.png', 'rb')

        file = open("%s/%s" % (self.test_directory, filename), "wb")
        file.write(file_content.read())
        file.close()

        # When
        write_file_to_directory(self.test_directory,
                                filename,
                                file_content)

        # Then
        expected_filename = "%s/%s_%s" % (self.test_directory, filename, str(1))
        assert os.path.exists(expected_filename)

    def test_write_files_to_directory_increment_filename_when_already_two_files_with_same_ean13(self):
        # Given
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)

        filename = 'image_id'
        file_content = open('static/images/default_thumb.png', 'rb')

        first_filename = "%s/%s" % (self.test_directory, filename)
        file = open(first_filename, "wb")
        file.write(file_content.read())
        file.close()

        second_filename = first_filename + "_1"
        file = open(second_filename, "wb")
        file.write(file_content.read())
        file.close()

        # When
        write_file_to_directory(self.test_directory,
                                filename,
                                file_content)

        # Then
        expected_filename = "%s/%s_%s" % (self.test_directory, filename, str(2))
        assert os.path.exists(expected_filename)

    def test_get_all_sub_directories_return_2_directories(self):
        # Given
        sub_directory_1 = '/tmp/test_directory/dir_1/'
        sub_directory_2 = '/tmp/test_directory/dir_2/'
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)
            os.makedirs(sub_directory_1)
            os.makedirs(sub_directory_2)

        # When
        sub_directories = get_all_sub_directories(self.test_directory)

        # Then
        assert sub_directories == [sub_directory_1, sub_directory_2]

    def test_extract_book_ean13_returns_ean13_from_filename(self):
        # Given
        thumb_filename = "test_directory/images/000/1304800000000_1_75.jpg"

        # When
        ean13 = extract_book_ean13(thumb_filename)

        # Then
        assert ean13 == '1304800000000'
