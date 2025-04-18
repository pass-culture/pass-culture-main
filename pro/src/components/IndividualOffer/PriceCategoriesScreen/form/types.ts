import { hasProperties } from 'commons/utils/types'

export type PriceCategoryForm = {
  label: string
  price: number | ''
  id?: number
}

export const isPriceCategoriesForm = (
  value: unknown
): value is PriceCategoryForm => hasProperties(value, ['label', 'price'])

export type PriceCategoriesFormValues = {
  priceCategories: PriceCategoryForm[]
  isDuo: boolean
}

export const isPriceCategoriesFormValues = (
  value: unknown
): value is PriceCategoriesFormValues =>
  hasProperties(value, ['priceCategories', 'isDuo']) &&
  Array.isArray(value.priceCategories) &&
  value.priceCategories.every(isPriceCategoriesForm)
