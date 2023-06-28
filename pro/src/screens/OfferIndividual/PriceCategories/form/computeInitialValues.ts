import { OfferIndividual } from 'core/Offers/types'

import { FIRST_INITIAL_PRICE_CATEGORY } from './constants'
import { PriceCategoriesFormValues, PriceCategoryForm } from './types'

export const sortPriceCategories = (
  a: PriceCategoryForm,
  b: PriceCategoryForm
) => {
  if (a.price === '' || b.price === '') {
    return 1
  }
  return b.price - a.price
}

export const computeInitialValues = (
  offer: OfferIndividual
): PriceCategoriesFormValues => {
  const initialPriceCategories =
    !offer.priceCategories || offer?.priceCategories.length === 0
      ? [FIRST_INITIAL_PRICE_CATEGORY]
      : offer.priceCategories

  initialPriceCategories.sort(sortPriceCategories)

  return {
    priceCategories: initialPriceCategories,
    isDuo: Boolean(offer.isDuo),
  }
}
