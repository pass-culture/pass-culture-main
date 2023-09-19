import * as yup from 'yup'

import { getNthParentFormValues } from 'utils/yupValidationTestHelpers'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './constants'
import { isPriceCategoriesForm, isPriceCategoriesFormValues } from './types'

const priceCategoryValidationSchema = yup.object().shape({
  label: yup
    .string()
    .required('Veuillez renseigner un intitulé de tarif')
    .max(PRICE_CATEGORY_LABEL_MAX_LENGTH, 'Le nom du tarif est trop long')
    .test(
      'priceCategoryDuplication',
      'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
      function test() {
        const allFormValues = getNthParentFormValues(this, 1)
        const currentPriceCategoryFormValues = getNthParentFormValues(this, 0)

        if (
          !isPriceCategoriesFormValues(allFormValues) ||
          !isPriceCategoriesForm(currentPriceCategoryFormValues)
        ) {
          throw new yup.ValidationError("Le formulaire n'est pas complet")
        }

        if (
          currentPriceCategoryFormValues.label === '' ||
          currentPriceCategoryFormValues.label === undefined ||
          currentPriceCategoryFormValues.price === '' ||
          currentPriceCategoryFormValues.price === undefined
        ) {
          return true
        }

        return (
          allFormValues.priceCategories.filter(
            priceCategory =>
              priceCategory.label === currentPriceCategoryFormValues.label &&
              priceCategory.price === currentPriceCategoryFormValues.price
          ).length === 1
        )
      }
    ),
  price: yup
    .number()
    .required('Veuillez renseigner un tarif')
    .min(0, 'Le prix ne peut pas être inferieur à 0€')
    .max(
      PRICE_CATEGORY_PRICE_MAX,
      `Veuillez renseigner un tarif inférieur à ${PRICE_CATEGORY_PRICE_MAX}€`
    ),
})

export const validationSchema = yup.object().shape({
  priceCategories: yup
    .array()
    .of(priceCategoryValidationSchema)
    .required()
    .min(1),
  isDuo: yup.boolean(),
})
