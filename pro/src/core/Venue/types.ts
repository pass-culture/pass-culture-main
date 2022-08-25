import { GetVenueResponseModel } from 'apiClient/v1'
import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import { IAccessibiltyFormValues } from 'core/shared'

// TODO use api/gen types
export interface IAPIVenue {
  address: string
  audioDisabilityCompliant: boolean
  bannerMeta: string | null
  bannerUrl: string | null
  bic: string
  bookingEmail: string
  businessUnitId: string
  city: string
  comment: null
  dateCreated: string
  dateModifiedAtLastProvider: string
  departementCode: string
  description: string
  fieldsUpdated: []
  iban: string
  id: string
  isPermanent: true
  isVirtual: boolean
  lastProviderId: null
  latitude: number
  longitude: number
  managingOffererId: string
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  nonHumanizedId: number
  nOffers: number
  name: string
  postalCode: string
  publicName: string
  pricingPoint: {
    id: number
    siret: string
    venueName: string
  }
  pricingPointId: number | null
  siret: string
  thumbCount: number
  venueLabelId: string | null
  venueTypeCode: string
  visualDisabilityCompliant: boolean
  withdrawalDetails: string | null
}

export type TOfferIndividualVenue = {
  id: string
  managingOffererId: string
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
  accessibility: IAccessibiltyFormValues
}

export type VenueCollectiveInformation = Pick<
  GetVenueResponseModel,
  | 'collectiveDescription'
  | 'collectiveDomains'
  | 'collectiveEmail'
  | 'collectiveInterventionArea'
  | 'collectiveLegalStatus'
  | 'collectiveNetwork'
  | 'collectivePhone'
  | 'collectiveStudents'
  | 'collectiveWebsite'
>

export interface IVenue {
  bannerMeta: IVenueBannerMetaProps | undefined
  bannerUrl: string
  contact: {
    email: string
    phoneNumber: string
    webSite: string
  }
  id: string
  isPermanent: boolean
  publicName: string
}
