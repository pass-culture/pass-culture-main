import { DEFAULT_PRICE_TABLE_ENTRY_LABEL_WHEN_SINGLE } from '../../IndividualOfferPriceTable/commons/constants'
import type { PriceCategoryForm } from './types'

export const PRICE_CATEGORY_LABEL_MAX_LENGTH = 50
export const PRICE_CATEGORY_MAX_LENGTH = 50

export const INITIAL_PRICE_CATEGORY: PriceCategoryForm = {
  label: '',
  price: '',
}

export const FIRST_INITIAL_PRICE_CATEGORY: PriceCategoryForm = {
  label: DEFAULT_PRICE_TABLE_ENTRY_LABEL_WHEN_SINGLE,
  price: '',
}
