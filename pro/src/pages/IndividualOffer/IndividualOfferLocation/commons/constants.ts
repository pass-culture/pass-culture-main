import type { LocationFormValues, PhysicalAddressSubformValues } from './types'

export const DEFAULT_PHYSICAL_ADDRESS_SUBFORM_INITIAL_VALUES: PhysicalAddressSubformValues =
  {
    addressAutocomplete: null,
    banId: null,
    city: null,
    coords: null,
    inseeCode: null,
    isManualEdition: false,
    latitude: null,
    locationLabel: null,
    longitude: null,
    offerLocation: null,
    postalCode: null,
    'search-addressAutocomplete': null,
    street: null,
  }

export const DEFAULT_LOCATION_FORM_INITIAL_VALUES: LocationFormValues = {
  ...DEFAULT_PHYSICAL_ADDRESS_SUBFORM_INITIAL_VALUES,
  url: null,
}
