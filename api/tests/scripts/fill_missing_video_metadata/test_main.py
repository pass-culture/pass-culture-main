from unittest import mock

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.connectors import youtube
from pcapi.scripts.fill_missing_video_metadata import main


pytestmark = pytest.mark.usefixtures("db_session")


@mock.patch("pcapi.connectors.youtube.get_video_metadata")
def test_fill_video_metadata(get_video_metadata_from_cache_mock):
    video_url_1 = "https://www.youtube.com/watch?v=XmVU35hbEA0"
    mock_id = "XmVU35hbEA0"
    mock_title = "So Few Words"
    mock_thumbnail_url = "https://example.com/high.jpg"
    mock_duration = 100

    video_url_2 = "https://www.youtube.com/watch?v=fl6kVK-B3OQ&list=RDfl6kVK-B3OQ&start_radio=1"
    video_id = "fl6kVK-B3OQ"
    video_title = "The Break"
    video_thumbnail_url = "https://example.com/low.jpg"
    video_duration = 200

    get_video_metadata_from_cache_mock.return_value = youtube.YoutubeVideoMetadata(
        id=mock_id,
        title=mock_title,
        thumbnail_url=mock_thumbnail_url,
        duration=mock_duration,
    )

    offer_with_video_without_metadata = offers_factories.OfferFactory()
    offers_factories.OfferMetaDataFactory(
        offer=offer_with_video_without_metadata,
        videoDuration=None,
        videoExternalId=None,
        videoThumbnailUrl=None,
        videoTitle=None,
        videoUrl=video_url_1,
    )

    offer_without_video_without_metadata = offers_factories.OfferFactory()
    assert offer_without_video_without_metadata.metaData is None

    offer_with_video_with_metadata = offers_factories.OfferFactory()
    offers_factories.OfferMetaDataFactory(
        offer=offer_with_video_with_metadata,
        videoDuration=video_duration,
        videoExternalId=video_id,
        videoThumbnailUrl=video_thumbnail_url,
        videoTitle=video_title,
        videoUrl=video_url_2,
    )

    main.main(not_dry=True)  # ...

    assert offer_with_video_without_metadata.metaData.videoUrl == video_url_1
    assert offer_with_video_without_metadata.metaData.videoExternalId == mock_id
    assert offer_with_video_without_metadata.metaData.videoThumbnailUrl == mock_thumbnail_url
    assert offer_with_video_without_metadata.metaData.videoTitle == mock_title
    assert offer_with_video_without_metadata.metaData.videoDuration == mock_duration

    assert offer_without_video_without_metadata.metaData is None

    assert offer_with_video_with_metadata.metaData.videoUrl == video_url_2
    assert offer_with_video_with_metadata.metaData.videoExternalId == video_id
    assert offer_with_video_with_metadata.metaData.videoThumbnailUrl == video_thumbnail_url
    assert offer_with_video_with_metadata.metaData.videoTitle == video_title
    assert offer_with_video_with_metadata.metaData.videoDuration == video_duration


@pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeNotFoundBackend")
def test_delete_video_metadata_when_video_is_private():
    video_url = "https://www.youtube.com/watch?v=XmVU35hbEA0"

    offer_with_video_without_metadata = offers_factories.OfferFactory()
    offers_factories.OfferMetaDataFactory(
        offer=offer_with_video_without_metadata,
        videoDuration=None,
        videoExternalId=None,
        videoThumbnailUrl=None,
        videoTitle=None,
        videoUrl=video_url,
    )

    main.main(not_dry=True)

    assert offer_with_video_without_metadata.metaData.videoUrl == None
    assert offer_with_video_without_metadata.metaData.videoExternalId == None
    assert offer_with_video_without_metadata.metaData.videoThumbnailUrl == None
    assert offer_with_video_without_metadata.metaData.videoTitle == None
    assert offer_with_video_without_metadata.metaData.videoDuration == None


def test_delete_video_metadata_when_url_is_incorect():
    video_url = "https://lundi.am/"

    offer_with_video_without_metadata = offers_factories.OfferFactory()
    offers_factories.OfferMetaDataFactory(
        offer=offer_with_video_without_metadata,
        videoDuration=None,
        videoExternalId=None,
        videoThumbnailUrl=None,
        videoTitle=None,
        videoUrl=video_url,
    )

    main.main(not_dry=True)
    assert offer_with_video_without_metadata.metaData.videoUrl == None
    assert offer_with_video_without_metadata.metaData.videoExternalId == None
    assert offer_with_video_without_metadata.metaData.videoThumbnailUrl == None
    assert offer_with_video_without_metadata.metaData.videoTitle == None
    assert offer_with_video_without_metadata.metaData.videoDuration == None
