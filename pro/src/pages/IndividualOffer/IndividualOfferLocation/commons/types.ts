export interface PhysicalAddressSubformValues {
  addressAutocomplete: string | null
  banId: string | null
  city: string | null
  coords: string | null
  inseeCode: string | null
  isManualEdition: boolean
  latitude: string | null
  locationLabel: string | null
  longitude: string | null
  offerLocation: string | null
  postalCode: string | null
  'search-addressAutocomplete': string | null
  street: string | null
}

export interface LocationFormValues extends PhysicalAddressSubformValues {
  url: string | null
}
