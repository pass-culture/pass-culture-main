import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../constants'
import type { LocationFormValues } from '../types'

export const makeLocationFormValues = <
  T extends Partial<
    Omit<LocationFormValues, 'location'> & {
      location: Partial<LocationFormValues['location']>
    }
  >,
>(
  overrides: T
): Omit<LocationFormValues, keyof T> & T => {
  return {
    location: overrides.location
      ? {
          ...EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES,
          ...overrides.location,
        }
      : null,
    url: overrides.url ?? null,
  } as Omit<LocationFormValues, keyof T> & T
}
