import { BannerMetaModel, GetVenueResponseModel } from 'apiClient/v1'
import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import { AccessiblityEnum } from 'core/shared'
import { IVenue } from 'core/Venue'

export const serializeVenueApi = (venue: GetVenueResponseModel): IVenue => {
  const venueAccessibility = {
    [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
  }
  return {
    accessibility: {
      ...venueAccessibility,
      [AccessiblityEnum.NONE]:
        !Object.values(venueAccessibility).includes(true),
    },
    address: venue.address || '',
    bannerMeta: venue.bannerMeta
      ? serializeBannerMetaApi(venue.bannerMeta)
      : null,
    bannerUrl: venue.bannerUrl || '',
    city: venue.city || '',
    comment: venue.comment || '',
    contact: {
      phoneNumber: venue.contact?.phoneNumber || '',
      email: venue.contact?.email || '',
      webSite: venue.contact?.website || '',
    },
    departmentCode: venue.departementCode || '',
    description: venue.description || '',
    id: venue.id,
    isPermanent: venue.isPermanent || false,
    isVenueVirtual: venue.isVirtual,
    latitude: venue.latitude || 0,
    longitude: venue.longitude || 0,
    mail: venue.bookingEmail || '',
    name: venue.name,
    publicName: venue.publicName || '',
    postalCode: venue.postalCode || '',
    siret: venue.siret || '',
    venueLabel: venue.venueLabelId || '',
    venueType: venue.venueTypeCode || '',
  }
}

const serializeBannerMetaApi = (
  apiBannerMeta: BannerMetaModel
): IVenueBannerMetaProps => {
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
