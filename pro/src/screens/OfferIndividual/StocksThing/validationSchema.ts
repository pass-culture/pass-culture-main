import * as yup from 'yup'

export const getValidationSchema = (
  /* istanbul ignore next: DEBT, TO FIX */
  minQuantity: number | null = null
) => {
  const validationSchema = {
    price: yup
      .number()
      .typeError('Veuillez renseigner un prix')
      .min(0, 'Le prix ne peut pas être inferieur à 0€')
      .max(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Veuillez renseigner un prix'),
    bookingLimitDatetime: yup.date().nullable(),
    quantity: yup
      .number()
      .nullable()
      .typeError('Doit être un nombre')
      .min(0, 'Doit être positif'),
    activationCodes: yup.array(),
    isDuo: yup.boolean(),
  }
  if (minQuantity !== null) {
    validationSchema.quantity = validationSchema.quantity.min(
      minQuantity,
      'Quantité trop faible'
    )
  }

  return yup.object().shape(validationSchema)
}
