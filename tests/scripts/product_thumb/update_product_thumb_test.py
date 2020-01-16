import os
from unittest.mock import MagicMock, patch

from repository.repository import Repository
from scripts.product_thumb.update_product_thumb import process_product_thumb, _compute_product_id_from_uri, \
    _get_product_thumb, \
    OBJECT_STORAGE_URL, process_file
from tests.conftest import clean_database
from tests.model_creators.specific_creators import create_product_with_thing_type
from tests.scripts.product_thumb.test_image_as_bytes import IMAGE_AS_BYTES
from utils.human_ids import humanize


class GetProductThumbTest:
    @patch('scripts.product_thumb.update_product_thumb.requests.get')
    def test_should_request_data_with_complete_object_storage_url(self, requests_get):
        # Given
        uri = 'thumbs/products/A6UQA'

        # When
        _get_product_thumb(uri)

        # Then
        thumb_storage_url = os.path.join(OBJECT_STORAGE_URL, uri)
        requests_get.assert_called_once_with(thumb_storage_url)

    @patch('scripts.product_thumb.update_product_thumb.requests.get')
    def test_should_return_product_thumb_when_status_code_200(self, requests_get):
        # Given
        uri = 'thumbs/products/A6UQA'
        requests_get.return_value = MagicMock(status_code=200, content=IMAGE_AS_BYTES)

        # When
        product_thumb = _get_product_thumb(uri)

        # Then
        assert product_thumb == IMAGE_AS_BYTES

    @patch('scripts.product_thumb.update_product_thumb.requests.get')
    @patch('scripts.product_thumb.update_product_thumb.logger.error')
    def test_should_log_error_with_uri_when_status_code_is_not_200(self, logger_error, requests_get):
        # Given
        uri = 'thumbs/products/A6UQA'
        requests_get.return_value = MagicMock(status_code=400)

        # When
        thumb = _get_product_thumb(uri)

        # Then
        logger_error.assert_called_once_with(f'[BATCH][PRODUCT THUMB UPDATE] Could not get thumb for uri {uri}')
        assert thumb is None


class ComputeProductIdFromUriTest:
    def test_should_extract_dehumanized_product_id_from_uri(self):
        # Given
        uri = 'thumbs/products/A6UQA'

        # When
        dehumanized_product_id = _compute_product_id_from_uri(uri)

        # Then
        assert dehumanized_product_id == 502016

    def test_should_extract_dehumanized_product_id_from_uri_when_product_thumb_is_not_the_first_one(self):
        # Given
        uri = 'thumbs/products/A6UQA_1'

        # When
        dehumanized_product_id = _compute_product_id_from_uri(uri)

        # Then
        assert dehumanized_product_id == 502016


class ProcessProductThumbTest:
    @clean_database
    def test_should_call_object_storage_connector_with_right_uri(self, app):
        # Given
        uri = 'thumbs/products/A6UQA'
        get_product_thumb = MagicMock()

        # When
        process_product_thumb(uri, get_product_thumb)

        # Then
        get_product_thumb.assert_called_once_with('thumbs/products/A6UQA')

    @clean_database
    @patch('scripts.product_thumb.update_product_thumb.logger.debug')
    def test_should_increase_product_thumb_count_by_one_and_set_first_thumb_dominant_color_when_thumb_is_main(self,
                                                                                                              logger_debug,
                                                                                                              app):
        # Given
        product = create_product_with_thing_type(thumb_count=0)
        Repository.save(product)
        human_product_id = humanize(product.id)
        uri = f'thumbs/products/{human_product_id}'
        get_product_thumb = MagicMock(return_value=IMAGE_AS_BYTES)

        # When
        updated_product = process_product_thumb(uri, get_product_thumb)

        # Then
        assert updated_product.thumbCount == 1
        logger_debug.assert_called_once_with(
            f'[BATCH][PRODUCT THUMB UPDATE] Product with id: "{product.id}" / uri: "{uri}" processed successfully')

    @clean_database
    def test_should_increase_product_thumb_count_by_one_and_not_set_first_thumb_dominant_color_when_thumb_is_not_main(
            self, app):
        # Given
        product = create_product_with_thing_type(thumb_count=1)
        Repository.save(product)
        human_product_id = humanize(product.id)
        uri = f'thumbs/products/{human_product_id}_1'
        get_product_thumb = MagicMock(return_value=IMAGE_AS_BYTES)

        # When
        updated_product = process_product_thumb(uri, get_product_thumb)

        # Then
        assert updated_product.thumbCount == 2

    @patch('scripts.product_thumb.update_product_thumb._compute_product_id_from_uri')
    def test_should_not_compute_product_id_for_uri_when_product_thumb_is_not_found(self, compute_product_id):
        # Given
        uri = 'thumbs/products/AE'
        get_product_thumb = MagicMock(return_value=None)

        # When
        success = process_product_thumb(uri, get_product_thumb)

        # Then
        compute_product_id.assert_not_called()
        assert not success

    @clean_database
    @patch('scripts.product_thumb.update_product_thumb.logger.debug')
    def test_should_log_error_when_product_does_not_exist_in_database(self, logger_debug, app):
        # Given
        uri = 'thumbs/products/AE'
        get_product_thumb = MagicMock(return_value=IMAGE_AS_BYTES)

        # When
        success = process_product_thumb(uri, get_product_thumb)

        # Then
        logger_debug.assert_called_once_with(
            f'[BATCH][PRODUCT THUMB UPDATE] Product not found for id: "1" / uri: "thumbs/products/AE"')
        assert not success

    @clean_database
    @patch('scripts.product_thumb.update_product_thumb.logger.debug')
    def test_should_log_error_when_product_thumb_count_is_zero_and_current_thumb_is_not_main(self, logger_debug, app):
        # Given
        product = create_product_with_thing_type(thumb_count=0)
        Repository.save(product)
        human_product_id = humanize(product.id)
        uri = f'thumbs/products/{human_product_id}_1'
        get_product_thumb = MagicMock(return_value=IMAGE_AS_BYTES)

        # When
        success = process_product_thumb(uri, get_product_thumb)

        # Then
        logger_debug.assert_called_once_with(
            f'[BATCH][PRODUCT THUMB UPDATE] Trying to process secondary thumb when main '
            f'thumb was not processed for product with id: "{product.id}" / uri: "{uri}"')
        assert not success

    @clean_database
    @patch('scripts.product_thumb.update_product_thumb.logger.debug')
    def test_should_not_fetch_product_thumb_when_is_not_main(self, logger_debug, app):
        # Given
        product = create_product_with_thing_type(thumb_count=1)
        Repository.save(product)
        human_product_id = humanize(product.id)
        uri = f'thumbs/products/{human_product_id}_1'
        get_product_thumb = MagicMock()

        # When
        success = process_product_thumb(uri, get_product_thumb)

        # Then
        get_product_thumb.assert_not_called()
        assert success
        logger_debug.assert_called_once_with(
            f'[BATCH][PRODUCT THUMB UPDATE] Product with id: "{product.id}" / uri: "{uri}" processed successfully')


class ProcessFileTest:
    def test_should_iterate_through_file_containing_product_thumbs_uris(self):
        # Given
        product_thumbs_uris_file_path = 'tests/scripts/product_thumb/test_product_thumbs_uris.txt'
        process_product_thumb = MagicMock()

        # When
        process_file(product_thumbs_uris_file_path, process_product_thumb)

        # Then
        assert process_product_thumb.call_count == 7
