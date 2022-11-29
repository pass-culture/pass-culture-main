import * as yup from 'yup'

import { getToday, removeTime } from 'utils/date'

const isBeforeBeginningDate = (
  bookingLimitDatetime: Date | undefined | null,
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
      .required('Champ obligatoire')
      .min(removeTime(getToday()), "L'évènement doit être à venir"),
    beginningTime: yup.string().nullable().required('Champ obligatoire'),
    price: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif')
      .max(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Champ obligatoire'),
    bookingLimitDatetime: yup.date().nullable().test({
      name: 'bookingLimitDatetime-before-beginningDate',
      message: 'Date invalide',
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
