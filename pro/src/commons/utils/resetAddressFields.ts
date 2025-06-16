import { UseFormResetField } from 'react-hook-form'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { AddressFormValues } from 'commons/core/shared/types'

const fieldsNames: Map<keyof AddressFormValues, string | null> = new Map([
  ['street', ''],
  ['postalCode', ''],
  ['city', ''],
  ['latitude', ''],
  ['longitude', ''],
  ['coords', ''],
  ['banId', ''], // TODO: See with backend if it's preferable to send also "null" to be consistent with "inseeCode"
  ['inseeCode', null],
  ['search-addressAutocomplete', ''],
  ['addressAutocomplete', ''],
])

export function resetReactHookFormAddressFields({
  resetField,
}: {
  resetField: UseFormResetField<OfferEducationalFormValues>
}) {
  ;[...fieldsNames.entries()].map(([fieldName, defaultValue]) =>
    resetField(fieldName, { defaultValue: defaultValue })
  )
}
