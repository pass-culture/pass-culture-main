import { PriceCategoryForm } from './types'

let priceCategoryFormId = 1
export const priceCategoryFormFactory = (): PriceCategoryForm => ({
  label: `Tarif ${priceCategoryFormId++}`,
  price: 20,
})
