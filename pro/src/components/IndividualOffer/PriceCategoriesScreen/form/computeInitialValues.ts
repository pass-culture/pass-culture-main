import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'

import { FIRST_INITIAL_PRICE_CATEGORY } from './constants'
import type { PriceCategoriesFormValues, PriceCategoryForm } from './types'
import { convertEuroToPacificFranc } from '@/commons/utils/convertEuroToPacificFranc'

const sortPriceCategories = (a: PriceCategoryForm, b: PriceCategoryForm) => {
  if (a.price === '' || b.price === '') {
    return 1
  }
  return b.price - a.price
}

export const computeInitialValues = (
  offer: GetIndividualOfferResponseModel,
  isCaledonian: boolean = false
): PriceCategoriesFormValues => {
  const initialPriceCategories =
    !offer.priceCategories || offer.priceCategories.length === 0
      ? [FIRST_INITIAL_PRICE_CATEGORY]
      : offer.priceCategories

  initialPriceCategories.sort(sortPriceCategories)

  return {
    priceCategories: initialPriceCategories.map((cat) => ({
      ...cat,
      price: isCaledonian
        ? convertEuroToPacificFranc(Number(cat.price))
        : cat.price,
    })),
    isDuo: Boolean(offer.isDuo),
  }
}
