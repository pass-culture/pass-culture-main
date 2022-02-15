import { Venue } from './venue'

export type OffererName = {
  id: string
  name: string
}

export type Offerer = {
  id: string
  postalCode: string
  dateCreated: Date
  name: string
  siren?: string
  bic?: string
  iban?: string
  demarchesSimplifieesApplicationId?: string
  dateModifiedAtLastProvider?: Date
  fieldsUpdated: string[]
  idAtProviders?: string
  isActive: boolean
  address?: string
  city: string
  isValidated: boolean
  userHasAccess: boolean
  dateValidated?: Date
  lastProviderId?: string
  nOffers: number
  thumbCount: number
  managedVenues: Venue[]
}
