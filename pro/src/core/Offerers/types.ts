import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  OffererApiKey,
} from 'apiClient/v1'

export type OffererName = GetOffererNameResponseModel

export interface Offerer extends GetOffererResponseModel {
  address?: string | null
  apiKey: OffererApiKey
  city: string
  dateCreated: string
  dateModifiedAtLastProvider?: string | null
  demarchesSimplifieesApplicationId?: string | null
  fieldsUpdated: Array<string>
  hasAvailablePricingPoints: boolean
  hasDigitalVenueAtLeastOneOffer: boolean
  hasValidBankAccount: boolean
  hasPendingBankAccount: boolean
  hasNonFreeOffer: boolean
  hasActiveOffer: boolean
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>
  idAtProviders?: string | null
  isActive: boolean
  isValidated: boolean
  lastProviderId?: string | null
  managedVenues: Array<GetOffererVenueResponseModel>
  name: string
  id: number
  postalCode: string
  siren: string
  dsToken: string
}
