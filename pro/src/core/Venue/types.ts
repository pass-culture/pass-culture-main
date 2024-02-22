import { DMSApplicationForEAC, GetVenueResponseModel } from 'apiClient/v1'
import { VenueBannerMetaProps } from 'components/VenueForm/ImageUploaderVenue/ImageUploaderVenue'
import { AccessibiltyFormValues } from 'core/shared'

export type IndividualOfferVenueItem = {
  id: number
  managingOffererId: number
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
  accessibility: AccessibiltyFormValues
  bookingEmail?: string | null
  hasMissingReimbursementPoint: boolean
  hasCreatedOffer: boolean
  venueType: string
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
  | 'collectiveSubCategoryId'
>

export interface Venue extends GetVenueResponseModel {
  accessibility: AccessibiltyFormValues
  bannerMeta: VenueBannerMetaProps | null | undefined
  collectiveDmsApplication: DMSApplicationForEAC | null
}

export type Providers = {
  id: number
  isActive: boolean
  name: string
  hasOffererProvider: boolean
}
