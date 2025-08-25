import { OFFER_LOCATION } from '../../commons/constants'
import type {
  NullableIfNonBoolean,
  PhysicalAddressSubformValues,
} from './types'

export const EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES: NullableIfNonBoolean<PhysicalAddressSubformValues> =
  {
    addressAutocomplete: null,
    banId: null,
    city: null,
    coords: null,
    inseeCode: null,
    isManualEdition: false,
    isVenueAddress: false,
    latitude: null,
    locationLabel: null,
    longitude: null,
    offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
    postalCode: null,
    'search-addressAutocomplete': null,
    street: null,
  }
