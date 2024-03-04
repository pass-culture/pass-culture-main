import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'

export type IndividualOfferVenueItem = VenueListItemResponseModel

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
