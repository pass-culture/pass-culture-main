import { OfferIndividual } from 'core/Offers/types'

import { FIRST_INITIAL_PRICE_CATEGORY } from './constants'
import { PriceCategoriesFormValues } from './types'

export const computeInitialValues = (
  offer: OfferIndividual
): PriceCategoriesFormValues => {
  const initialPriceCategories =
    !offer.priceCategories || offer?.priceCategories.length === 0
      ? [FIRST_INITIAL_PRICE_CATEGORY]
      : offer.priceCategories
  return {
    priceCategories: initialPriceCategories,
    isDuo: offer.isDuo,
  }
}
