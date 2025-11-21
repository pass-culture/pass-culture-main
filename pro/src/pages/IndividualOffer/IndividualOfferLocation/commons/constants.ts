import { OFFER_LOCATION } from '../../commons/constants'
import type { PhysicalAddressSubformValues } from './types'

export const EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES: PhysicalAddressSubformValues =
  {
    addressAutocomplete: null,
    banId: null,
    city: '',
    coords: '',
    inseeCode: null,
    isManualEdition: false,
    isVenueLocation: false,
    label: null,
    latitude: '',
    longitude: '',
    offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
    postalCode: '',
    'search-addressAutocomplete': null,
    street: null,
  }
