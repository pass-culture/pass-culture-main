import { isValid } from 'date-fns'
import * as yup from 'yup'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export const MAX_STOCKS_QUANTITY = 1000000

export const getValidationSchema = (
  mode: OFFER_WIZARD_MODE,
  /* istanbul ignore next: DEBT, TO FIX */
  bookingsQuantity: number,
  stockId?: number
) => {
  // Do not validate if there is no stock in edition
  // (so you can delete the last stock of a published offer)
  const shouldApplyValidationSchema =
    mode === OFFER_WIZARD_MODE.CREATION || stockId !== undefined

  return yup.object().shape({
    price: yup.number().when([], (_, schema) => {
      if (shouldApplyValidationSchema) {
        return schema
          .typeError('Veuillez renseigner un prix')
          .min(0, 'Le prix ne peut pas être inferieur à 0€')
          .max(300, 'Veuillez renseigner un prix inférieur à 300€')
          .required('Veuillez renseigner un prix')
      } else {
        return schema.optional()
      }
    }),
    bookingLimitDatetime: yup
      .string()
      .test((v) => (v ? isValid(new Date(v)) : true))
      .when([], (_, schema) => {
        if (shouldApplyValidationSchema) {
          return schema
            .nullable()
            .transform((curr, orig) => (orig === '' ? undefined : curr))
        } else {
          return schema.optional()
        }
      }),
    quantity: yup.number().when([], (_, schema) => {
      if (shouldApplyValidationSchema) {
        let min = bookingsQuantity > 0 ? bookingsQuantity : 0
        let minText =
          bookingsQuantity > 0
            ? 'Veuillez indiquer un nombre supérieur ou égal au nombre de réservations'
            : 'Doit être positif'
        if (mode === OFFER_WIZARD_MODE.CREATION) {
          min = 1
          minText = 'Veuillez indiquer un nombre supérieur à 0'
        }
        return schema
          .optional()
          .nullable()
          .typeError('Doit être un nombre')
          .transform((_, val) => (val || val === 0 ? Number(val) : null))
          .min(min, minText)
          .max(
            MAX_STOCKS_QUANTITY,
            'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
          )
      } else {
        return schema.optional()
      }
    }),
    activationCodes: yup.array(),
    isDuo: yup.boolean(),

    stockId: yup.number().optional(),
    bookingsQuantity: yup.string().optional(),
    remainingQuantity: yup.string().optional(),
    activationCodesExpirationDatetime: yup
      .string()
      .test((v) => (v ? isValid(new Date(v)) : true))
      .transform((curr, orig) => (orig === '' ? undefined : curr))
      .optional(),
  })
}
