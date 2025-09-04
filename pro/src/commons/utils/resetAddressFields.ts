import type { AddressFormValues } from '@/commons/core/shared/types'

const fieldsNames: Map<keyof AddressFormValues, string | null> = new Map([
  ['street', ''],
  ['postalCode', ''],
  ['city', ''],
  ['latitude', ''],
  ['longitude', ''],
  ['coords', ''],
  ['banId', null],
  ['inseeCode', null],
  ['search-addressAutocomplete', ''],
  ['addressAutocomplete', ''],
])

export function resetReactHookFormAddressFields(
  resetField: (name: any, defaultValue: any) => void
) {
  ;[...fieldsNames.entries()].map(([fieldName, defaultValue]) => {
    resetField(fieldName, defaultValue)
  })
}
