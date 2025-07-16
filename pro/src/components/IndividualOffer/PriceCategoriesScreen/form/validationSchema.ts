import * as yup from 'yup'

import { getNthParentFormValues } from 'commons/utils/yupValidationTestHelpers'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './constants'
import {
  isPriceCategoriesForm,
  isPriceCategoriesFormValues,
} from './types'

const labelTooLongMsg = 'Le nom du tarif est trop long'
const labelRequiredMsg = 'Veuillez renseigner un intitulé de tarif'
const labelDuplicateMsg =
  'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix'

const priceRequiredMsg = 'Veuillez renseigner un tarif'
const priceTooLowMsg = 'Le prix ne peut pas être inferieur à 0€'
const priceTooHighMsg = `Veuillez renseigner un tarif inférieur à ${PRICE_CATEGORY_PRICE_MAX}€`

const priceCategoryValidationSchema = yup.object({
  label: yup
    .string()
    .required(labelRequiredMsg)
    .max(PRICE_CATEGORY_LABEL_MAX_LENGTH, labelTooLongMsg)
    .test('no-duplicate', labelDuplicateMsg, function () {
      const allValues = getNthParentFormValues(this, 1)
      const current = getNthParentFormValues(this, 0)

      if (
        !isPriceCategoriesFormValues(allValues) ||
        !isPriceCategoriesForm(current)
      ) {
        throw new yup.ValidationError('Le formulaire n’est pas complet')
      }

      if (!current.label || !current.price) {return true}

      const duplicates = allValues.priceCategories.filter(
        (p) => p.label === current.label && p.price === current.price
      )

      return duplicates.length === 1
    }),

  price: yup
    .number()
    .nullable()
    .transform((value) => (Number.isNaN(value) ? null : value))
    .min(0, 'Nombre positif attendu')
    .required(priceRequiredMsg)
    .min(0, priceTooLowMsg)
    .max(PRICE_CATEGORY_PRICE_MAX, priceTooHighMsg),
})

export const validationSchema = yup.object({
  priceCategories: yup
    .array()
    .of(priceCategoryValidationSchema)
    .required()
    .min(1),
  isDuo: yup.boolean(),
})
