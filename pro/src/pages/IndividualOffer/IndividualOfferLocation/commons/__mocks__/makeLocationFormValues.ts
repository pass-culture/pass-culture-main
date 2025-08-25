import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../constants'
import type { LocationFormValues } from '../types'

export const makeLocationFormValues = <
  T extends Partial<
    Omit<LocationFormValues, 'address'> & {
      address: Partial<LocationFormValues['address']>
    }
  >,
>(
  overrides: T
): Omit<LocationFormValues, keyof T> & T => {
  return {
    address: overrides.address
      ? {
          ...EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES,
          ...overrides.address,
        }
      : null,
    url: overrides.url ?? null,
  } as Omit<LocationFormValues, keyof T> & T
}
