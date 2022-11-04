import { BannerMetaModel, GetVenueResponseModel } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'
import { IVenue } from 'core/Venue'
import { IVenueBannerMetaProps } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'

export const serializeVenueApi = (venue: GetVenueResponseModel): IVenue => {
  const venueAccessibility = {
    [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
  }
  /* istanbul ignore next: DEBT, TO FIX */
  return {
    demarchesSimplifieesApplicationId:
      venue.demarchesSimplifieesApplicationId || null,
    hasPendingBankInformationApplication:
      venue.hasPendingBankInformationApplication != null
        ? venue.hasPendingBankInformationApplication
        : null,
    managingOfferer: venue.managingOfferer || [],
    reimbursementPointId: venue.reimbursementPointId || null,
    nonHumanizedId: venue.nonHumanizedId || 0,
    pricingPoint: venue.pricingPoint || null,
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
      phoneNumber: venue.contact?.phoneNumber || null,
      email: venue.contact?.email || null,
      webSite: venue.contact?.website || null,
    },
    departmentCode: venue.departementCode || '',
    description: venue.description || '',
    collectiveDomains: venue.collectiveDomains || [],
    dateCreated: venue.dateCreated || '',
    fieldsUpdated: venue.fieldsUpdated || '',
    isVirtual: venue.isVirtual || false,
    managingOffererId: venue.managingOffererId || '',
    dmsToken: venue.dmsToken || '',
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
    venueLabel: venue.venueLabelId || null,
    venueType: venue.venueTypeCode || '',
    withdrawalDetails: venue.withdrawalDetails || '',
    collectiveAccessInformation: venue.collectiveAccessInformation || '',
    collectiveDescription: venue.collectiveDescription || '',
    collectiveEmail: venue.collectiveEmail || '',
    collectiveInterventionArea: venue.collectiveInterventionArea || [],
    collectiveLegalStatus: venue.collectiveLegalStatus || null,
    collectiveNetwork: venue.collectiveNetwork || [],
    collectivePhone: venue.collectivePhone || '',
    collectiveStudents: venue.collectiveStudents || [],
    collectiveWebsite: venue.collectiveWebsite || '',
  }
}

const serializeBannerMetaApi = (
  apiBannerMeta: BannerMetaModel
): IVenueBannerMetaProps => {
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
