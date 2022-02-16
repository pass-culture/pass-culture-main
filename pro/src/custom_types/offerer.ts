export type OffererName = {
  id: string
  name: string
}

export type Offerer = {
  address?: string
  apiKey: {
    maxAllowed: number
    prefixes: string[]
  }
  bic?: string
  city: string
  dateCreated: Date
  dateModifiedAtLastProvider?: Date
  demarchesSimplifieesApplicationId?: string
  fieldsUpdated: string[]
  hasDigitalVenueAtLeastOneOffer: boolean
  hasMissingBankInformation: boolean
  iban?: string
  id: string
  idAtProviders?: string
  isValidated: boolean
  lastProviderId?: string
  managedVenues: ManagedVenue[]
  name: string
  postalCode: string
  siren?: string
}

export type OffererListItem = {
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
  managedVenues: ManagedVenue[]
}

export type EducationalOfferer = {
  id: string
  name: string
  managedVenues: EducationalManagedVenue[]
}

type EducationalManagedVenue = {
  address?: string
  city?: string
  id: string
  isVirtual: boolean
  publicName?: string
  name: string
  postalCode?: string
  audioDisabilityCompliant?: boolean
  mentalDisabilityCompliant?: boolean
  motorDisabilityCompliant?: boolean
  visualDisabilityCompliant?: boolean
}

type ManagedVenue = EducationalManagedVenue & {
  bookingEmail?: string
  businessUnitId?: number
  comment?: string
  departementCode?: string
  isValidated: boolean
  managingOffererId: string
  venueLabelId?: string
  withdrawalDetails?: string
}
