import type {
  FieldValues,
  Path,
  PathValue,
  UseFormReturn,
} from 'react-hook-form'

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

export function resetReactHookFormAddressFields<
  TFieldValues extends FieldValues,
>(resetField: UseFormReturn<TFieldValues>['setValue']) {
  fieldsNames.entries().forEach(([fieldName, defaultValue]) => {
    resetField(
      fieldName as Path<TFieldValues>,
      defaultValue as PathValue<TFieldValues, Path<TFieldValues>>
    )
  })
}
