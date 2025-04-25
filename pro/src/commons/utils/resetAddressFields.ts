import { type FormikContextType } from 'formik'

import { AddressFormValues } from 'commons/core/shared/types'

const fieldsNames: Array<keyof AddressFormValues> = [
  'street',
  'postalCode',
  'city',
  'latitude',
  'longitude',
  'coords',
  'banId',
  'search-addressAutocomplete',
  'addressAutocomplete',
]

export const resetAddressFields = async <FormValues>({
  formik,
}: {
  formik: FormikContextType<FormValues>
}) => {
  // Empty all fields value
  await Promise.all(
    fieldsNames.map((fieldName) => formik.setFieldValue(fieldName, ''))
  )

  // Make all fields untouched
  // (This will prevent validation errors to be shown if user previously touched those fields, then switched that trigger OFF, then ON again)
  await Promise.all(
    fieldsNames.map((fieldName) => formik.setFieldTouched(fieldName, false))
  )
}
