import * as yup from 'yup'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBeforeEventDate = (
  bookingLimitDatetime: Date | undefined,
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

export const validationSchema = yup.object().shape({
  eventDate: yup
    .date()
    .nullable()
    .required('Champ requis')
    .min(
      todayAtMidnight(),
      "La date de l'évènement doit être supérieure à aujourd'hui"
    ),
  eventTime: yup.string().nullable().required('Champ requis'),
  numberOfPlaces: yup
    .number()
    .nullable()
    .min(0, 'Nombre positif attendu')
    .required('Champ requis'),
  totalPrice: yup
    .number()
    .nullable()
    .min(0, 'Nombre positif attendu')
    .required('Champ requis'),
  bookingLimitDatetime: yup
    .date()
    .notRequired()
    .test({
      name: 'is-one-true',
      message:
        'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
      test: isBeforeEventDate,
    })
    .nullable(),
  priceDetail: yup.string().nullable().max(1000),
})

export const showcaseOfferValidationSchema = yup
  .object()
  .shape({ priceDetail: yup.string().nullable().max(1000) })
