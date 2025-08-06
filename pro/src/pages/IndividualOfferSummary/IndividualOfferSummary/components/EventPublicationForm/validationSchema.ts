import { addYears, isBefore, isSameDay, startOfDay } from 'date-fns'
import * as yup from 'yup'

import { isDateValid } from 'commons/utils/date'
import { buildDateTime } from 'components/IndividualOffer/StocksEventEdition/serializers'

function isDateInFuture(value: string) {
  const dateTime = isDateValid(value) && buildDateTime(value, '00:00')

  return dateTime && !isBefore(dateTime, startOfDay(new Date()))
}

function isDateWithinTwoYears(value: string) {
  const twoYearsFromNow = addYears(new Date(), 2)

  return isDateValid(value) && new Date(value) < twoYearsFromNow
}

function isDateTimeInFuture(value: string, date: string) {
  if (!value || !isDateValid(date)) {
    return false
  }
  const dateTime = buildDateTime(date, value)
  const now = new Date()

  //  Invalid when the date is today and the time is in the past
  return !isBefore(dateTime, now) || !isSameDay(dateTime, now)
}

export const publicationDateValidationSchema = (schema: yup.StringSchema) =>
  schema.when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une date de publication')
        .test(
          'is-date-in-future',
          'Veuillez indiquer une date dans le futur',
          isDateInFuture
        )
        .test(
          'is-within-two-years',
          'Veuillez indiquer une date dans les 2 ans à venir',
          isDateWithinTwoYears
        ),
  })

export const publicationTimeValidationSchema = (schema: yup.StringSchema) =>
  schema.when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une heure de publication')
        .test(
          'is-time-in-future',
          'Veuillez indiquer une heure dans le futur',
          (value, context) =>
            isDateTimeInFuture(value, context.parent.publicationDate)
        ),
  })

export const bookingAllowedDateValidationSchema = (schema: yup.StringSchema) =>
  schema.when('bookingAllowedMode', {
    is: (bookingAllowedMode: string) => bookingAllowedMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une date de réservabilité')
        .test(
          'is-date-in-future',
          'Veuillez indiquer une date dans le futur',
          isDateInFuture
        )
        .test(
          'is-within-two-years',
          'Veuillez indiquer une date dans les 2 ans à venir',
          isDateWithinTwoYears
        ),
  })

export const bookingAllowedTimeValidationSchema = (schema: yup.StringSchema) =>
  schema.when('bookingAllowedMode', {
    is: (bookingAllowedMode: string) => bookingAllowedMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une heure de réservabilité')
        .test(
          'is-time-in-future',
          'Veuillez indiquer une heure dans le futur',
          (value, context) =>
            isDateTimeInFuture(value, context.parent.bookingAllowedDate)
        ),
  })

export const validationSchema = yup.object().shape({
  publicationMode: yup.string<'now' | 'later'>().required(),
  publicationDate: publicationDateValidationSchema(yup.string()),
  publicationTime: publicationTimeValidationSchema(yup.string()),
  bookingAllowedMode: yup.string<'now' | 'later'>().required(),
  bookingAllowedDate: bookingAllowedDateValidationSchema(yup.string()),
  bookingAllowedTime: bookingAllowedTimeValidationSchema(yup.string()),
})
