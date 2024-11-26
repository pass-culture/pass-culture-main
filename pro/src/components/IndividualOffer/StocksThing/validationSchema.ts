import * as yup from 'yup'

import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'

export const MAX_STOCKS_QUANTITY = 1000000

export const getValidationSchema = (
  mode: OFFER_WIZARD_MODE,
  /* istanbul ignore next: DEBT, TO FIX */
  bookingsQuantity: number,
  stockId?: number,
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
      .min(
        mode === OFFER_WIZARD_MODE.EDITION ? 0 : 1,
        mode === OFFER_WIZARD_MODE.EDITION ? 'Doit être positif' : 'Veuillez indiquer un nombre supérieur à 0'
      )
      .max(
        MAX_STOCKS_QUANTITY,
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
      ),
    activationCodes: yup.array(),
    isDuo: yup.boolean(),
  }

  if (mode === OFFER_WIZARD_MODE.EDITION && bookingsQuantity > 0) {
    validationSchema.quantity = validationSchema.quantity.min(
      bookingsQuantity,
      'Veuillez indiquer un nombre supérieur ou égal au nombre de réservations'
    )
  }

  // Do not validate if there is no stock in edition
  // (so you can delete the last stock of a published offer)
  const shouldApplyValidationSchema = mode === OFFER_WIZARD_MODE.CREATION || stockId !== undefined
  return yup.object().shape(shouldApplyValidationSchema ? validationSchema : {})
}
