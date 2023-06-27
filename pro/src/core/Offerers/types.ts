import {
  GetOffererNameResponseModel,
  GetOffererVenueResponseModel,
  OffererApiKey,
} from 'apiClient/v1'

export type OffererName = GetOffererNameResponseModel

export interface Offerer {
  address?: string | null
  apiKey: OffererApiKey
  city: string
  dateCreated: string
  dateModifiedAtLastProvider?: string | null
  demarchesSimplifieesApplicationId?: string | null
  fieldsUpdated: Array<string>
  hasAvailablePricingPoints: boolean
  hasDigitalVenueAtLeastOneOffer: boolean
  id: string
  idAtProviders?: string | null
  isActive: boolean
  isValidated: boolean
  lastProviderId?: string | null
  managedVenues: Array<GetOffererVenueResponseModel>
  name: string
  nonHumanizedId: number
  postalCode: string
  siren: string
}
