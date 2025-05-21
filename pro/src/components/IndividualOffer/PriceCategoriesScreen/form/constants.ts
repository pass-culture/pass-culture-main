import { PriceCategoryForm } from './types'

export const PRICE_CATEGORY_LABEL_MAX_LENGTH = 50
export const PRICE_CATEGORY_MAX_LENGTH = 50

export const PRICE_CATEGORY_PRICE_MAX = 300

export const INITIAL_PRICE_CATEGORY: PriceCategoryForm = {
  label: '',
  price: '',
}

export const UNIQUE_PRICE = 'Tarif unique'

export const FIRST_INITIAL_PRICE_CATEGORY: PriceCategoryForm = {
  label: UNIQUE_PRICE,
  price: '',
}
