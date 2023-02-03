import * as yup from 'yup'

import { getNthParentFormValues } from 'utils/yupValidationTestHelpers'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './constants'
import { isPriceCategoriesFormValues } from './types'

export const priceCategoryValidationSchema = yup.object().shape({
  label: yup
    .string()
    .required('Veuillez renseigner un intitulé de tarif')
    .max(PRICE_CATEGORY_LABEL_MAX_LENGTH, 'Le nom du tarif est trop long')
    .test(
      'labelDuplication',
      'Veuillez renseigner des intitulés différents',
      function test(value) {
        const allFormValues = getNthParentFormValues(this, 1)

        if (!isPriceCategoriesFormValues(allFormValues)) {
          throw new yup.ValidationError("Le formulaire n'est pas complet")
        }

        return (
          allFormValues.priceCategories.filter(
            priceCategory => priceCategory.label === value
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
