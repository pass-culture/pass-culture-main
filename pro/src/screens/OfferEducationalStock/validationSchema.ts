import { isSameDay } from 'date-fns'
import * as yup from 'yup'

import { MAX_DETAILS_LENGTH } from 'core/OfferEducational/constants'

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
    .max(60000, 'Le prix ne doit pas dépasser 60 000€')
    .required('Champ requis')
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
      .required('Champ requis')
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
      .required('Champ requis')
      .when([], {
        is: () => !preventPriceIncrease,
        then: (schema) =>
          schema.min(
            todayAtMidnight(),
            "La date de l’évènement doit être supérieure à aujourd'hui"
          ),
      }),
    eventTime: yup
      .string()
      .nullable()
      .required('Champ requis')
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
      .min(0, 'Nombre positif attendu')
      .max(3000, 'Le nombre de participants ne doit pas dépasser 3000')
      .required('Champ requis'),
    totalPrice: totalPriceValidation,
    bookingLimitDatetime: yup
      .date()
      .required('La date limite de réservation est obligatoire')
      .test({
        name: 'is-one-true',
        message:
          'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
        test: (value, context) => isBeforeEventDate(value, context),
      })
      .nullable(),
    priceDetail: yup.string().required('Champ requis').max(MAX_DETAILS_LENGTH),
  })
}

export const showcaseOfferValidationSchema = yup
  .object()
  .shape({ priceDetail: yup.string().nullable().max(MAX_DETAILS_LENGTH) })
