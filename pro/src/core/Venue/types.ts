import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'

export type IndividualOfferVenueItem = VenueListItemResponseModel & {
  id: number
  managingOffererId: number
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
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
>

export type Providers = {
  id: number
  isActive: boolean
  name: string
  hasOffererProvider: boolean
}
