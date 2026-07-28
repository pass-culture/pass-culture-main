import { addYears, isBefore, isSameDay, startOfDay } from 'date-fns'

import { buildDateTime, isDateValid } from '@/commons/utils/date'

import type { yup } from '.'

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

function isDateBeforeFirstBookingLimit(
  value: string,
  firstBookingLimitDatetime: string
) {
  if (!value || !isDateValid(value)) {
    return false
  }
  if (!firstBookingLimitDatetime) {
    return true
  }
  const dateTime = buildDateTime(value, '00:00')
  const firstBookingLimitDate = new Date(firstBookingLimitDatetime)
  if (Number.isNaN(firstBookingLimitDate.getTime())) {
    return true
  }

  return (
    isBefore(dateTime, firstBookingLimitDate) ||
    isSameDay(dateTime, firstBookingLimitDate)
  )
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
        )
        .test(
          'is-before-first-booking-limit',
          'Veuillez indiquer une date avant la date limite de réservation',
          (value, context) =>
            isDateBeforeFirstBookingLimit(
              value,
              context.options.context?.firstBookingLimitDatetime
            )
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
        )
        .test(
          'is-before-first-booking-limit',
          'Veuillez indiquer une date avant la date limite de réservation',
          (value, context) =>
            isDateBeforeFirstBookingLimit(
              value,
              context.options.context?.firstBookingLimitDatetime
            )
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
