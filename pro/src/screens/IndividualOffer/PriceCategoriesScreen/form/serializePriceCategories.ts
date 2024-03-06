import { PriceCategoryBody } from 'apiClient/v1'

import { PriceCategoriesFormValues } from '../form/types'

export const serializePriceCategories = (
  values: PriceCategoriesFormValues
): PriceCategoryBody => {
  const serializedData = values.priceCategories.map((priceCategory) => {
    if (priceCategory.price === '') {
      throw new Error('Price should not be empty because of formik validation')
    }
    return {
      label: priceCategory.label,
      price: priceCategory.price,
      id: priceCategory.id,
    }
  })
  return {
    priceCategories: serializedData,
  }
}
