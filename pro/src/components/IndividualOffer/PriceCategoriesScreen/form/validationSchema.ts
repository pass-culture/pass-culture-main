import * as yup from 'yup'

import { getNthParentFormValues } from '@/commons/utils/yupValidationTestHelpers'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './constants'
import { isPriceCategoriesForm, isPriceCategoriesFormValues } from './types'

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

      if (!current.label || (!current.price && current.price !== 0)) {
        return true
      }

      const duplicates = allValues.priceCategories.filter((p) => {
        return p.label === current.label && p.price === current.price
      })

      return duplicates.length === 1
    }),

  price: yup
    .mixed<number | ''>()
    .test('is-valid-price', 'Le prix doit être un nombre', (value) =>
      value === '' ? true : typeof value === 'number'
    )
    .test('min', priceTooLowMsg, (value) =>
      typeof value === 'number' ? value >= 0 : false
    )
    .test('max', priceTooHighMsg, (value) =>
      typeof value === 'number' ? value <= PRICE_CATEGORY_PRICE_MAX : false
    )
    .transform((value) => (value === '' ? undefined : value))
    .required(priceRequiredMsg),
})

export const validationSchema = yup.object({
  priceCategories: yup
    .array()
    .of(priceCategoryValidationSchema)
    .required()
    .min(1),
  isDuo: yup.boolean(),
})
