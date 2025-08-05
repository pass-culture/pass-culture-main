import { isDateValid } from 'commons/utils/date'
import { buildDateTime } from 'components/IndividualOffer/StocksEventEdition/serializers'
import { addYears, isAfter } from 'date-fns'
import * as yup from 'yup'

export const publicationDateValidationSchema = (schema: yup.StringSchema) =>
  schema.when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une date de publication')
        .test(
          'is-in-future',
          'Veuillez indiquer une date dans le futur',
          (value, context) => {
            const dateTime =
              isDateValid(value) && context.parent.publicationTime
                ? buildDateTime(value, context.parent.publicationTime)
                : undefined

            return dateTime && isAfter(dateTime, new Date())
          }
        )
        .test(
          'is-within-two-years',
          'Veuillez indiquer une date dans les 2 ans à venir',
          (value) => {
            const twoYearsFromNow = addYears(new Date(), 2)

            return isDateValid(value) && new Date(value) < twoYearsFromNow
          }
        ),
  })

export const publicationTimeValidationSchema = (schema: yup.StringSchema) =>
  schema.when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema.required('Veuillez sélectionner une heure de publication'),
  })

export const bookingAllowedDateValidationSchema = (schema: yup.StringSchema) =>
  schema.when('bookingAllowedMode', {
    is: (bookingAllowedMode: string) => bookingAllowedMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une date de réservabilité')
        .test(
          'is-in-future',
          'Veuillez indiquer une date dans le futur',
          (value, context) => {
            const dateTime =
              isDateValid(value) && context.parent.bookingAllowedTime
                ? buildDateTime(value, context.parent.bookingAllowedTime)
                : undefined
            return dateTime && isAfter(dateTime, new Date())
          }
        )
        .test(
          'is-within-two-years',
          'Veuillez indiquer une date dans les 2 ans à venir',
          (value) => {
            const twoYearsFromNow = addYears(new Date(), 2)

            return isDateValid(value) && new Date(value) < twoYearsFromNow
          }
        ),
  })

export const bookingAllowedTimeValidationSchema = (schema: yup.StringSchema) =>
  schema.when('bookingAllowedMode', {
    is: (bookingAllowedMode: string) => bookingAllowedMode === 'later',
    then: (schema) =>
      schema.required('Veuillez sélectionner une heure de réservabilité'),
  })

export const validationSchema = yup.object().shape({
  publicationMode: yup.string<'now' | 'later'>().required(),
  publicationDate: publicationDateValidationSchema(yup.string()),
  publicationTime: publicationTimeValidationSchema(yup.string()),
  bookingAllowedMode: yup.string<'now' | 'later'>().required(),
  bookingAllowedDate: bookingAllowedDateValidationSchema(yup.string()),
  bookingAllowedTime: bookingAllowedTimeValidationSchema(yup.string()),
})
