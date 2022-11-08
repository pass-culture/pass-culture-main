import * as yup from 'yup'

import { getToday, removeTime } from 'utils/date'

const isBeforeBeginningDate = (
  bookingLimitDatetime: Date | undefined,
  context: yup.TestContext
) => {
  if (!context.parent.beginningDate || !bookingLimitDatetime) {
    return true
  }
  return bookingLimitDatetime <= context.parent.beginningDate
}

const getSingleValidationSchema = (minQuantity: number | null = null) => {
  const validationSchema = {
    beginningDate: yup
      .date()
      .nullable()
      .required('Veuillez renseigner une date')
      .min(removeTime(getToday()), "L'évènement doit être à venir"),
    beginningTime: yup
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
      .typeError('Veuillez renseigner une date')
      .test({
        name: 'bookingLimitDatetime-before-beginningDate',
        message: "Veuillez rentrer une date antérieur à la date de l'évènement",
        test: isBeforeBeginningDate,
      }),

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

  return validationSchema
}

export const getValidationSchema = (minQuantity: number | null = null) => {
  const validationSchema = {
    stocks: yup
      .array()
      .of(yup.object().shape(getSingleValidationSchema(minQuantity))),
  }

  return yup.object().shape(validationSchema)
}
