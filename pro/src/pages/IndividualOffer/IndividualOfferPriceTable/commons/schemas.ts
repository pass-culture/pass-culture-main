import { isValid } from 'date-fns'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { yup } from '@/commons/utils/yup'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
import { readonly } from '@/commons/utils/yup/readonly'

import {
  PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH,
  PRICE_TABLE_ENTRY_MAX_PRICE_IN_EUR,
  PRICE_TABLE_ENTRY_MAX_PRICE_IN_XPF,
  PRICE_TABLE_ENTRY_MAX_QUANTITY,
} from './constants'
import type { PriceTableEntryModel, PriceTableFormContext } from './types'

export const PriceTableEntryValidationSchema = yup.object().shape({
  // -------------------------------------------------------------------------
  // Readonly Data

  id: yup.number().transform(readonly).optional(),
  bookingsQuantity: yup.number().transform(readonly).optional(),
  offerId: yup.number().transform(readonly).defined(),
  remainingQuantity: yup
    .mixed<number | string>() // `number | "unlimited"`
    .nullable()
    .transform(readonly),

  // -------------------------------------------------------------------------
  // Updatable Data

  activationCodes: yup
    .array(yup.string().defined())
    .nullable()
    .default(null)
    .defined(),
  activationCodesExpirationDatetime: nonEmptyStringOrNull()
    .test((v) => (v ? isValid(new Date(v)) : true))
    .optional(),

  bookingLimitDatetime: nonEmptyStringOrNull().test((v) =>
    v ? isValid(new Date(v)) : true
  ),

  label: nonEmptyStringOrNull().when(['$offer'], (vals, schema) => {
    const [offer] = vals as [PriceTableFormContext['offer']]

    if (offer.isEvent) {
      return schema
        .required('Veuillez renseigner un intitulé de tarif')
        .max(
          PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH,
          'Le nom du tarif est trop long'
        )
    }

    return schema.optional()
  }),

  price: yup
    .number()
    .nullable()
    .default(null)
    .defined()
    .when(['$isCaledonian'], (vals, schema) => {
      const [isCaledonian] = vals as [PriceTableFormContext['isCaledonian']]

      return schema
        .typeError('Veuillez renseigner un prix')
        .min(
          0,
          isCaledonian
            ? 'Le prix ne peut pas être inférieur à 0F'
            : 'Le prix ne peut pas être inferieur à 0€'
        )
        .max(
          isCaledonian
            ? PRICE_TABLE_ENTRY_MAX_PRICE_IN_XPF
            : PRICE_TABLE_ENTRY_MAX_PRICE_IN_EUR,
          isCaledonian
            ? `Veuillez renseigner un prix inférieur à ${PRICE_TABLE_ENTRY_MAX_PRICE_IN_XPF} F`
            : `Veuillez renseigner un prix inférieur à ${PRICE_TABLE_ENTRY_MAX_PRICE_IN_EUR} €`
        )
        .required('Veuillez renseigner un prix')
    }),

  quantity: yup
    .number()
    .nullable()
    .default(null)
    .defined()
    .when(['$mode', 'bookingsQuantity'], (vals, schema) => {
      const [mode, bookingsQuantity] = vals as [
        PriceTableFormContext['mode'],
        PriceTableEntryModel['bookingsQuantity'],
      ]

      let min = bookingsQuantity && bookingsQuantity > 0 ? bookingsQuantity : 0
      let minText =
        bookingsQuantity && bookingsQuantity > 0
          ? 'Veuillez indiquer un nombre supérieur ou égal au nombre de réservations'
          : 'Doit être positif'
      if (mode === OFFER_WIZARD_MODE.CREATION) {
        min = 1
        minText = 'Veuillez indiquer un nombre supérieur à 0'
      }

      return schema
        .optional()
        .typeError('Doit être un nombre')
        .min(min, minText)
        .max(
          PRICE_TABLE_ENTRY_MAX_QUANTITY,
          'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
        )
    }),
})

export type PriceTableEntryFormValues = yup.InferType<
  typeof PriceTableEntryValidationSchema
>

export const PriceTableValidationSchema = yup.object().shape({
  entries: yup
    .array()
    .of(PriceTableEntryValidationSchema)
    .min(1)
    .defined()
    .uniqueBy(
      'label',
      'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
      (item) => `${item.label}-${item.price}`
    ),
  isDuo: yup
    .boolean()
    .nullable()
    .default(null)
    .defined()
    .when(['$offer'], (vals, schema) => {
      const [offer] = vals as [PriceTableFormContext['offer']]

      return offer.isEvent ? schema.default(true).defined() : schema.optional()
    }),
})

export type PriceTableFormValues = yup.InferType<
  typeof PriceTableValidationSchema
>
