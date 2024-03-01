export interface VenueSettingsFormValues {
  address: string
  addressAutocomplete: string
  banId: string
  bookingEmail: string
  city: string
  comment: string
  isWithdrawalAppliedOnAllOffers: boolean
  latitude: number
  longitude: number
  name: string
  postalCode: string
  publicName: string
  reimbursementPointId: number | string | null
  'search-addressAutocomplete': string
  siret: string
  venueSiret: number | null
  venueType: string
  withdrawalDetails: string
}
