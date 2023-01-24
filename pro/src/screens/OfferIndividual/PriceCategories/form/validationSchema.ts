import * as yup from 'yup'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './constants'

export const priceCategoryValidationSchema = yup.object().shape({
  label: yup
    .string()
    .required('Veuillez renseigner un intitulé de tarif')
    .max(PRICE_CATEGORY_LABEL_MAX_LENGTH, 'Le nom du tarif est trop long'),
  price: yup
    .number()
    .required('Veuillez renseigner un tarif')
    .positive()
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
