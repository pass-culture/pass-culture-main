import { INITIAL_PRICE_CATEGORY } from './constants'
import { PriceCategoriesFormValues } from './types'

export const computeInitialValues = (): PriceCategoriesFormValues => {
  return {
    priceCategories: [INITIAL_PRICE_CATEGORY],
    isDuo: true,
  }
}
