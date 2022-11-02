import { endOfDay } from 'date-fns'
import * as yup from 'yup'

import { getToday } from 'utils/date'

const isBeforeEventDate = (
  bookingLimitDatetime: Date | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.beginningDate || !bookingLimitDatetime) {
    return true
  }

  if (
    bookingLimitDatetime.toLocaleDateString() ===
    context.parent.beginningDate.toLocaleDateString()
  ) {
    return true
  }

  return bookingLimitDatetime < context.parent.beginningDate
}

export const getValidationSchema = (minQuantity: number | null = null) => {
  const validationSchema = {
    beginningDate: yup
      .date()
      .required()
      .nullable()
      .required('Veuillez renseigner une date')
      .min(
        endOfDay(getToday()),
        "La date de l'évènement doit être supérieure à aujourd'hui"
      ),
    beginningTime: yup.string().required('Veuillez renseigner un horaire'),
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
        name: 'bookingLimitDatetime-before-beginningDate',
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
