import { PriceCategoryForm } from './types'

let priceCategoryFormId = 1
export const priceCategoryFormFactory = (
  customPriceCategory: Partial<PriceCategoryForm> = {}
): PriceCategoryForm => ({
  label: `Tarif ${priceCategoryFormId++}`,
  price: 20,
  ...customPriceCategory,
})
