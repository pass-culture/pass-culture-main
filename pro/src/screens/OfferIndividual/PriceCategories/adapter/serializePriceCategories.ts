import { PriceCategoryBody } from 'apiClient/v1'

import { PriceCategoriesFormValues } from '../form/types'

export const serializePriceCategories = (
  values: PriceCategoriesFormValues
): PriceCategoryBody => {
  const serializedData = values.priceCategories.map(priceCategory => ({
    // FIX ME remove "as" it 's here because of initial type that don't match api type
    label: priceCategory.label,
    price: priceCategory.price as number,
    id: priceCategory.id,
  }))

  return {
    priceCategories: serializedData,
  }
}
