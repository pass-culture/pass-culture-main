export const DEFAULT_ADDRESS_FORM_VALUES = {
  addressAutocomplete: '',
  banId: '',
  'search-addressAutocomplete': '',
  city: '',
  latitude: 0,
  longitude: 0,
  street: '',
  postalCode: '',
  inseeCode: '',
  coords: '',
  manuallySetAddress: false,
}

export const DEFAULT_OFFERER_FORM_VALUES = {
  siret: '',
  name: '',
  publicName: '',
  hasVenueWithSiret: false,
  ...DEFAULT_ADDRESS_FORM_VALUES,
  isOpenToPublic: '',
}
