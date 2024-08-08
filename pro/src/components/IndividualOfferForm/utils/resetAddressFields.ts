import { type FormikContextType } from 'formik'

import { type IndividualOfferFormValues } from '../types'

const fieldsNames = [
  'street',
  'postalCode',
  'city',
  'latitude',
  'longitude',
  'coords',
  'banId',
  'locationLabel',
  'search-addressAutocomplete',
  'addressAutocomplete',
]

export const resetAddressFields = async ({
  formik,
}: {
  formik: FormikContextType<IndividualOfferFormValues>
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
