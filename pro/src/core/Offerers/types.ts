import { GetOffererNameResponseModel } from 'apiClient/v1'

import { IAPIVenue } from '../Venue/types'

export type TOffererName = GetOffererNameResponseModel

export interface IAPIOfferer {
  address: string | null
  apiKey: {
    maxAllowed: number
    prefixes: string[]
  }
  bic: string | null
  city: string | null
  dateCreated: string | null
  dateModifiedAtLastProvider: string | null
  demarchesSimplifieesApplicationId: string | null
  fieldsUpdated: []
  hasAvailablePricingPoints: boolean
  hasDigitalVenueAtLeastOneOffer: boolean
  hasMissingBankInformation: boolean
  iban: string | null
  id: string
  isValidated: boolean
  lastProviderId: string | null
  managedVenues: IAPIVenue[]
  name: string
  postalCode: string | null
  siren: string
}
