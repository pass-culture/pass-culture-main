import json
import logging
from unittest import mock

import pytest

from pcapi.connectors import youtube
from pcapi.core.offers import factories as offers_factories
from pcapi.core.videos import api
from pcapi.core.videos import exceptions
from pcapi.utils.requests import ExternalAPIException


@pytest.mark.usefixtures("db_session")
class VideoIdExtractionTest:
    @pytest.mark.parametrize(
        "url,video_id",
        [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/e/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLUMRshJ8e2c4oQ60D4Ew15A1LgN5C7Y3X", "dQw4w9WgXcQ"),
        ],
    )
    def test_extract_youtube_video_id_from_url(self, url, video_id):
        assert api.extract_video_id(url) == video_id

    @pytest.mark.parametrize(
        "video_url",
        [
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ"),  # we do not accept shorts
            ("https://www.youtube.com/@Msnight_fall"),  # we do not accept channels
            ("https://www.youtube.com.jesuiscool.fr"),  # we do not accept subdomains, even if you are cool
            "https://vimeo.com/1078258590",
            "https://www.other.com",
            "dQw4w9WgXcQ",
            "https://www.youtube.comjesuisunvilainhacker",  # we do not accept hackers
            "m.youtube.com/watch?v=dQw4w9WgXcQ",  # we require https://
            "www.youtube.com/embed/dQw4w9WgXcQ",
            "youtube.com/v/dQw4w9WgXcQ",
            "ghtps://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ],
    )
    def test_extract_youtube_video_id_from_unsupported_url_should_raise(self, video_url):
        with pytest.raises(exceptions.InvalidVideoUrl) as error:
            assert api.extract_video_id(video_url)
        assert (
            str(error.value)
            == "The video URL must be from the Youtube plateform, it should be public and should not be a short nor a user's profile."
        )


@pytest.mark.usefixtures("db_session")
class GetVideoMetadataFromCacheTest:
    VIDEO_ID = "WtM4OW2qVjY"

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeExceptionBackend")
    def test_get_video_metadata_from_cache_with_data_in_cache(self, app):
        video_url = f"https://www.youtube.com/watch?v={self.VIDEO_ID}"
        video_id = api.extract_video_id(video_url)
        app.redis_client.set(
            f"{api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )
        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == video_id
        assert video_metadata.title == "Title"
        assert video_metadata.thumbnail_url == "thumbnail url"
        assert video_metadata.duration == 100

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeTestingBackend")
    def test_get_video_metadata_from_cache_without_data_in_cache(self):
        video_url = f"https://www.youtube.com/watch?v={self.VIDEO_ID}"

        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == self.VIDEO_ID
        assert video_metadata.title == "Mock Video Title"
        assert video_metadata.thumbnail_url == f"https://example.com/vi/{self.VIDEO_ID}/default.jpg"
        assert video_metadata.duration == 300

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeExceptionBackend")
    def test_get_video_metadata_from_cache_without_data_in_cache_connector_raise_error(self):
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"

        with pytest.raises(ExternalAPIException):
            api.get_video_metadata_from_cache(video_url)


@pytest.mark.usefixtures("db_session")
class UpsertVideoAndMetadataTest:
    GET_METADATA = "pcapi.core.videos.api.get_video_metadata_from_cache"
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    VIDEO_METADATA = youtube.YoutubeVideoMetadata(
        id="dQw4w9WgXcQ",
        title="Les Quatre Cents Coups, bande annonce",
        thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        duration=132,
    )

    def read_log(self, caplog):
        [record] = [r for r in caplog.records if getattr(r, "technical_message_id", "").startswith("offer.video.")]
        return record

    @mock.patch(GET_METADATA)
    def test_should_create_the_metadata_when_the_offer_has_none(self, get_video_metadata_from_cache):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        offer = offers_factories.OfferFactory()
        assert offer.metaData is None

        api.upsert_video_and_metadata(self.VIDEO_URL, offer)

        assert offer.metaData is not None

    @mock.patch(GET_METADATA)
    def test_should_store_the_metadata_returned_by_the_cache(self, get_video_metadata_from_cache):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        offer = offers_factories.OfferFactory()

        api.upsert_video_and_metadata(self.VIDEO_URL, offer)

        get_video_metadata_from_cache.assert_called_once_with(self.VIDEO_URL)
        assert offer.metaData.videoUrl == self.VIDEO_URL
        assert offer.metaData.videoExternalId == "dQw4w9WgXcQ"
        assert offer.metaData.videoTitle == "Les Quatre Cents Coups, bande annonce"
        assert offer.metaData.videoThumbnailUrl == "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
        assert offer.metaData.videoDuration == 132

    @mock.patch(GET_METADATA)
    def test_should_replace_the_metadata_of_a_video_that_is_already_there(self, get_video_metadata_from_cache):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        meta_data = offers_factories.OfferMetaDataFactory(
            videoUrl="https://www.youtube.com/watch?v=WtM4OW2qVjY", videoTitle="Jules et Jim", videoDuration=90
        )

        api.upsert_video_and_metadata(self.VIDEO_URL, meta_data.offer)

        assert meta_data.videoUrl == self.VIDEO_URL
        assert meta_data.videoTitle == "Les Quatre Cents Coups, bande annonce"
        assert meta_data.videoDuration == 132

    @mock.patch(GET_METADATA)
    def test_should_log_an_addition_when_the_offer_had_no_metadata(self, get_video_metadata_from_cache, caplog):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        offer = offers_factories.OfferFactory()

        with caplog.at_level(logging.INFO):
            api.upsert_video_and_metadata(self.VIDEO_URL, offer, provider_id=12)

        log = self.read_log(caplog)
        assert log.technical_message_id == "offer.video.added"
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "video_url": self.VIDEO_URL,
            "provider_id": 12,
        }

    @mock.patch(GET_METADATA)
    def test_should_log_an_addition_when_the_metadata_carried_no_video(self, get_video_metadata_from_cache, caplog):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        meta_data = offers_factories.OfferMetaDataFactory(videoUrl=None)

        with caplog.at_level(logging.INFO):
            api.upsert_video_and_metadata(self.VIDEO_URL, meta_data.offer)

        assert self.read_log(caplog).technical_message_id == "offer.video.added"

    @mock.patch(GET_METADATA)
    def test_should_log_an_update_when_the_offer_already_had_a_video(self, get_video_metadata_from_cache, caplog):
        get_video_metadata_from_cache.return_value = self.VIDEO_METADATA
        meta_data = offers_factories.OfferMetaDataFactory(videoUrl="https://www.youtube.com/watch?v=WtM4OW2qVjY")

        with caplog.at_level(logging.INFO):
            api.upsert_video_and_metadata(self.VIDEO_URL, meta_data.offer)

        assert self.read_log(caplog).technical_message_id == "offer.video.updated"


@pytest.mark.usefixtures("db_session")
class RemoveVideoDataFromOfferMetadataTest:
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def build_meta_data(self):
        return offers_factories.OfferMetaDataFactory(
            videoUrl=self.VIDEO_URL,
            videoDuration=132,
            videoExternalId="dQw4w9WgXcQ",
            videoThumbnailUrl="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            videoTitle="Les Quatre Cents Coups, bande annonce",
        )

    def test_should_clear_every_video_field(self):
        meta_data = self.build_meta_data()
        offer = meta_data.offer

        api.remove_video_data_from_offer_metadata(meta_data, offer.id, offer.venueId, self.VIDEO_URL)

        assert meta_data.videoUrl is None
        assert meta_data.videoDuration is None
        assert meta_data.videoExternalId is None
        assert meta_data.videoThumbnailUrl is None
        assert meta_data.videoTitle is None

    def test_should_log_the_deletion(self, caplog):
        meta_data = self.build_meta_data()
        offer = meta_data.offer

        with caplog.at_level(logging.INFO):
            api.remove_video_data_from_offer_metadata(meta_data, offer.id, offer.venueId, self.VIDEO_URL, 12)

        [log] = [r for r in caplog.records if getattr(r, "technical_message_id", None) == "offer.video.deleted"]
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "video_url": self.VIDEO_URL,
            "provider_id": 12,
        }
