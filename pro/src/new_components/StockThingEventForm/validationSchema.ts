import * as yup from 'yup'
import { ObjectShape } from 'yup/lib/object'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBeforeEventDate = (
  bookingLimitDatetime: Date | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.eventDatetime || !bookingLimitDatetime) {
    return true
  }

  if (
    bookingLimitDatetime.toLocaleDateString() ===
    context.parent.eventDatetime.toLocaleDateString()
  ) {
    return true
  }

  return bookingLimitDatetime < context.parent.eventDate
}

export const getValidationSchema = (minQuantity: number | null = null) => {
  const validationSchema = {
    eventDatetime: yup
      .date()
      .required()
      .nullable()
      .required('Veuillez renseigner une date')
      .min(
        todayAtMidnight(),
        "La date de l'évènement doit être supérieure à aujourd'hui"
      ),
    eventTime: yup
      .string()
      .nullable()
      .required('Veuillez renseigner un horaire'),
    price: yup
      .number()
      .typeError('Veuillez renseigner un prix')
      .moreThan(-1, 'Le prix ne peut pas être inferieur à 0€')
      .max(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Veuillez renseigner un prix'),
    bookingLimitDatetime: yup
      .date()
      .notRequired()
      .test({
        name: 'is-one-true',
        message: "Veuillez rentrer une date antérieur à la date de l'évènement",
        test: isBeforeEventDate,
      })
      .nullable(),
    quantity: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif'),
  }

  if (minQuantity !== null) {
    validationSchema.quantity = validationSchema.quantity.min(
      minQuantity,
      'Quantité trop faible'
    )
  }

  return yup.object().shape(validationSchema)
}

export const getValidationSchemaArray = (minQuantity: number | null = null) => {
  const validationSchema = getValidationSchema(minQuantity)
  return yup.object().shape({
    events: yup.array().of(validationSchema),
  })
}
