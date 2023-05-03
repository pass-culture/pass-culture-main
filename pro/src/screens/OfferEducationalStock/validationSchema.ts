import { isBefore, isSameDay } from 'date-fns'
import * as yup from 'yup'

import { MAX_DETAILS_LENGTH } from 'core/OfferEducational'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBeforeEventDate = (
  bookingLimitDatetime: Date | null | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.eventDate || !bookingLimitDatetime) {
    return true
  }

  if (
    bookingLimitDatetime.toLocaleDateString() ===
    context.parent.eventDate.toLocaleDateString()
  ) {
    return true
  }

  return bookingLimitDatetime < context.parent.eventDate
}

export const generateValidationSchema = (
  preventPriceIncrease: boolean,
  initialPrice: number | ''
) => {
  let totalPriceValidation = yup
    .number()
    .nullable()
    .min(0, 'Nombre positif attendu')
    .required('Champ requis')
  if (preventPriceIncrease && initialPrice) {
    totalPriceValidation = totalPriceValidation.max(
      initialPrice,
      'Vous ne pouvez pas définir un prix plus élevé.'
    )
  }

  return yup.object().shape({
    eventDate: yup
      .date()
      .nullable()
      .required('Champ requis')
      .when([], {
        is: () => preventPriceIncrease === false,
        then: schema =>
          schema.min(
            todayAtMidnight(),
            "La date de l’évènement doit être supérieure à aujourd'hui"
          ),
      }),
    eventTime: yup
      .string()
      .nullable()
      .required('Champ requis')
      .when('eventDate', {
        is: (eventDate: string) => isSameDay(new Date(eventDate), new Date()),
        then: schema =>
          schema.test({
            name: 'is-before-current-time',
            test: (eventTime: string) =>
              isBefore(new Date(), new Date(eventTime)),
            message: "L'heure doit être postérieure à l'heure actuelle",
          }),
      }),
    numberOfPlaces: yup
      .number()
      .nullable()
      .min(0, 'Nombre positif attendu')
      .required('Champ requis'),
    totalPrice: totalPriceValidation,
    bookingLimitDatetime: yup
      .date()
      .notRequired()
      .test({
        name: 'is-one-true',
        message:
          'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
        test: (value, context) => isBeforeEventDate(value, context),
      })
      .nullable(),
    priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH),
  })
}

export const showcaseOfferValidationSchema = yup
  .object()
  .shape({ priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH) })
