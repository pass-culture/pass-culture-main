import * as yup from 'yup'

import { getToday, removeTime } from 'utils/date'

const isBeforeBeginningDate = (
  bookingLimitDatetime: Date | undefined | null,
  context: yup.TestContext
) => {
  if (
    !context.parent.beginningDate ||
    !bookingLimitDatetime ||
    context.parent.readOnlyFields.includes('beginningDate')
  ) {
    return true
  }
  return bookingLimitDatetime <= context.parent.beginningDate
}

const getSingleValidationSchema = () => {
  const validationSchema = {
    beginningDate: yup
      .date()
      .nullable()
      .required('Champ obligatoire')
      .when(['readOnlyFields'], (readOnlyFields, schema) => {
        /* istanbul ignore next: DEBT, TO FIX */
        if (readOnlyFields.includes('beginningDate')) {
          return schema
        }
        return schema.min(
          removeTime(getToday()),
          "L'évènement doit être à venir"
        )
      }),
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
    bookingsQuantity: yup.number(),
    quantity: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif')
      .when(['bookingsQuantity'], (bookingsQuantity, schema) => {
        const bookingQuantityNumber = parseInt(bookingsQuantity, 10)
        if (!isNaN(bookingQuantityNumber)) {
          return schema.min(bookingQuantityNumber, 'Quantité trop faible')
        }
        return schema
      }),
  }

  return validationSchema
}

export const getValidationSchema = () => {
  const validationSchema = {
    stocks: yup.array().of(yup.object().shape(getSingleValidationSchema())),
  }

  return yup.object().shape(validationSchema)
}
