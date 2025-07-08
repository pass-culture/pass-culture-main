import { isAfter, isBefore, isSameDay } from 'date-fns'
import * as yup from 'yup'

import { MAX_PRICE_DETAILS_LENGTH } from 'commons/core/OfferEducational/constants'

import { getMaxEndDateInSchoolYear } from './utils/getMaxEndDateInSchoolYear'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBookingDateBeforeStartDate = (
  bookingLimitDatetime: Date | null | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.startDatetime || !bookingLimitDatetime) {
    return true
  }

  return (
    isBefore(bookingLimitDatetime, context.parent.startDatetime) ||
    isSameDay(bookingLimitDatetime, context.parent.startDatetime)
  )
}

function isBookingDateAfterNow(
  bookingLimitDatetime: string | null | undefined
) {
  if (!bookingLimitDatetime) {
    return true
  }

  return !isBefore(bookingLimitDatetime, todayAtMidnight())
}

export const generateValidationSchema = (
  preventPriceIncrease: boolean,
  initialPrice: number | null,
  isReadOnly: boolean
) => {
  let totalPriceValidation = yup
    .number()
    .nullable()
    .transform((value) => (Number.isNaN(value) ? null : value))
    .min(0, 'Nombre positif attendu')
    .max(60000, 'Le prix ne doit pas dépasser 60 000€')
    .required('Le prix total TTC est obligatoire')
  if (preventPriceIncrease && initialPrice) {
    totalPriceValidation = totalPriceValidation.max(
      initialPrice,
      'Vous ne pouvez pas définir un prix plus élevé.'
    )
  }

  return yup.object().shape({
    startDatetime: yup
      .string()
      .required('La date de début est obligatoire')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema.test(
            'is-after-today',
            "La date de l’évènement doit être supérieure à aujourd'hui",
            function (startDate) {
              return !isBefore(startDate, todayAtMidnight())
            }
          ),
      }),
    endDatetime: yup
      .string()
      .required('La date de fin est obligatoire')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema
            .test(
              'is-after-today',
              "La date de l’évènement doit être supérieure à aujourd'hui",
              function (endDate) {
                return !isBefore(endDate, todayAtMidnight())
              }
            )
            .test(
              'is-same-year',
              'Les dates doivent être sur la même année scolaire',
              function (endDate) {
                return !isAfter(
                  endDate,
                  getMaxEndDateInSchoolYear(this.parent.startDatetime)
                )
              }
            ),
      }),
    eventTime: yup
      .string()
      .required('L’horaire est obligatoire')
      .when('startDatetime', {
        is: (startDatetime: string) =>
          isSameDay(new Date(startDatetime), new Date()) &&
          !preventPriceIncrease,
        then: (schema) =>
          schema.test({
            name: 'is-before-current-time',
            test: (eventTime: string) => {
              const date = new Date()
              const [hours, minutes] = eventTime.split(':')
              date.setHours(Number(hours))
              date.setMinutes(Number(minutes))

              return new Date().getTime() < date.getTime()
            },
            message: "L'heure doit être postérieure à l'heure actuelle",
          }),
      }),
    numberOfPlaces: yup
      .number()
      .transform((value) => (Number.isNaN(value) ? null : value))
      .min(1, 'Minimum 1 participant')
      .max(3000, 'Le nombre de participants ne doit pas dépasser 3000')
      .nullable()
      .required('Le nombre de participants est obligatoire'),
    totalPrice: totalPriceValidation,
    bookingLimitDatetime: yup
      .string()
      .required('La date limite de réservation est obligatoire')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema
            .test(
              'is-before-event',
              'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
              function (bookingDate) {
                return isBookingDateBeforeStartDate(new Date(bookingDate), this)
              }
            )
            .test(
              'is-after-today',
              'La date limite de réservation doit être égale ou postérieure à la date actuelle',
              function (endDate) {
                return isReadOnly || isBookingDateAfterNow(endDate)
              }
            ),
      }),
    priceDetail: yup
      .string()
      .required('L’information sur le prix est obligatoire')
      .max(MAX_PRICE_DETAILS_LENGTH),
  })
}
