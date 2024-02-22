import { BannerMetaModel, GetVenueResponseModel } from 'apiClient/v1'
import { VenueBannerMetaProps } from 'components/VenueForm/ImageUploaderVenue/ImageUploaderVenue'
import { Venue } from 'core/Venue/types'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

export const serializeVenueApi = (venue: GetVenueResponseModel): Venue => {
  /* istanbul ignore next: DEBT, TO FIX */
  return {
    ...venue,
    bannerMeta: venue.bannerMeta
      ? serializeBannerMetaApi(venue.bannerMeta)
      : null,
    collectiveDmsApplication: getLastCollectiveDmsApplication(
      venue.collectiveDmsApplications
    ),
  }
}

const serializeBannerMetaApi = (
  apiBannerMeta: BannerMetaModel
): VenueBannerMetaProps => {
  /* istanbul ignore next: DEBT, TO FIX */
  return {
    image_credit: apiBannerMeta.image_credit || '',
    original_image_url: apiBannerMeta.original_image_url || '',
    crop_params: {
      x_crop_percent: apiBannerMeta.crop_params?.x_crop_percent || 0,
      y_crop_percent: apiBannerMeta.crop_params?.y_crop_percent || 0,
      width_crop_percent: apiBannerMeta.crop_params?.width_crop_percent || 0,
      height_crop_percent: apiBannerMeta.crop_params?.height_crop_percent || 0,
    },
  }
}
