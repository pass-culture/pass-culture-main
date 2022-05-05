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
  nOffers: number
  name: string
  postalCode: string
  publicName: string
  siret: string
  thumbCount: number
  venueLabelId: string | null
  venueTypeCode: string
  visualDisabilityCompliant: boolean
  withdrawalDetails: null
}

export type TOfferIndividualVenue = {
  id: string
  managingOffererId: string
  name: string
}
