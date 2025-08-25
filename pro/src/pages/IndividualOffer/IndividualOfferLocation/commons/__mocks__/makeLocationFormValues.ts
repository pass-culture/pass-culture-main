import type { LocationFormValues } from '../types'

export const makeLocationFormValues = <T extends Partial<LocationFormValues>>(
  overrides: T
) =>
  ({
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
    url: null,
    ...overrides,
  }) as Omit<LocationFormValues, keyof T> & T
