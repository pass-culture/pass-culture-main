import { isBefore, isSameDay } from 'date-fns'
import * as yup from 'yup'

import { MAX_DETAILS_LENGTH } from 'core/OfferEducational/constants'

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

  if (
    bookingLimitDatetime.toLocaleDateString() ===
    context.parent.startDatetime.toLocaleDateString()
  ) {
    return true
  }

  return bookingLimitDatetime < context.parent.startDatetime
}

function isBookingDateAfterNow(bookingLimitDatetime: Date | null | undefined) {
  if (!bookingLimitDatetime) {
    return true
  }

  return !isBefore(new Date(bookingLimitDatetime), todayAtMidnight())
}

export const generateValidationSchema = (
  preventPriceIncrease: boolean,
  initialPrice: number | ''
) => {
  let totalPriceValidation = yup
    .number()
    .nullable()
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
      .date()
      .nullable()
      .required('La date de début est obligatoire')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema.min(
            todayAtMidnight(),
            "La date de l’évènement doit être supérieure à aujourd'hui"
          ),
      }),
    endDatetime: yup
      .date()
      .nullable()
      .required('La date de fin est obligatoire')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema
            .min(
              todayAtMidnight(),
              "La date de l’évènement doit être supérieure à aujourd'hui"
            )
            .test({
              message: 'Les dates doivent être sur la même année scolaire',
              test: (value, context) =>
                value <=
                getMaxEndDateInSchoolYear(context.parent.startDatetime),
            }),
      }),
    eventTime: yup
      .string()
      .nullable()
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
      .nullable()
      .min(1, 'Minimum 1 participant')
      .max(3000, 'Le nombre de participants ne doit pas dépasser 3000')
      .required('Le nombre de participants est obligatoire'),
    totalPrice: totalPriceValidation,
    bookingLimitDatetime: yup
      .date()
      .required('La date limite de réservation est obligatoire')
      .test({
        message:
          'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
        test: (value, context) => isBookingDateBeforeStartDate(value, context),
      })
      .test({
        message:
          'La date limite de réservation doit être égale ou postérieure à la date actuelle',
        test: isBookingDateAfterNow,
      }),
    priceDetail: yup
      .string()
      .required('L’information sur le prix est obligatoire')
      .max(MAX_DETAILS_LENGTH),
  })
}

export const showcaseOfferValidationSchema = yup
  .object()
  .shape({ priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH) })
