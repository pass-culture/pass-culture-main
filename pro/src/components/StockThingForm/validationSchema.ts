import * as yup from 'yup'

export const getValidationSchema = (
  /* istanbul ignore next: DEBT, TO FIX */
  minQuantity: number | null = null
) => {
  const validationSchema = {
    price: yup
      .number()
      .typeError('Veuillez renseigner un prix')
      .moreThan(-1, 'Le prix ne peut pas être inferieur à 0€')
      .max(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Veuillez renseigner un prix'),
    bookingLimitDatetime: yup.date().nullable(),
    quantity: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif'),
    activationCodes: yup.array(),
  }
  if (minQuantity !== null) {
    validationSchema.quantity = validationSchema.quantity.min(
      minQuantity,
      'Quantité trop faible'
    )
  }

  return yup.object().shape(validationSchema)
}
