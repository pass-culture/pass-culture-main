import * as yup from 'yup'

import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'

export const MAX_STOCKS_QUANTITY = 1000000

export const getValidationSchema = (
  mode: OFFER_WIZARD_MODE,
  /* istanbul ignore next: DEBT, TO FIX */
  minQuantity: number
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
      .min(0, 'Doit être positif')
      .max(
        MAX_STOCKS_QUANTITY,
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
      ),
    activationCodes: yup.array(),
    isDuo: yup.boolean(),
  }

  if (minQuantity !== 0) {
    validationSchema.quantity = validationSchema.quantity.min(
      minQuantity,
      'Quantité trop faible'
    )
  }

  return yup.object().when('stockId', {
    // Do not validate if there is no stock in edition
    // (so you can delete the last stock of a published offer)
    is: (stockId: string | undefined) =>
      mode === OFFER_WIZARD_MODE.CREATION || stockId !== undefined,
    then: (schema) => schema.shape(validationSchema),
  })
}
