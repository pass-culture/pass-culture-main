import { type FormikContextType } from 'formik'

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

export const resetAddressFields = async <FormValues>({
  formik,
}: {
  formik: FormikContextType<FormValues>
}) => {
  await Promise.all(
    [...fieldsNames.entries()].map(([fieldName, defaultValue]) =>
      formik.setFieldValue(fieldName, defaultValue)
    )
  )

  // Make all fields untouched
  // (This will prevent validation errors to be shown if user previously touched those fields, then switched that trigger OFF, then ON again)
  await Promise.all(
    [...fieldsNames.keys()].map((fieldName) =>
      formik.setFieldTouched(fieldName, false)
    )
  )
}