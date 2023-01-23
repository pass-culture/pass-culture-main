import { IOfferIndividual } from 'core/Offers/types'

import { INITIAL_PRICE_CATEGORY } from './constants'
import { PriceCategoriesFormValues } from './types'

export const computeInitialValues = (
  offer: IOfferIndividual
): PriceCategoriesFormValues => {
  return {
    priceCategories: [INITIAL_PRICE_CATEGORY],
    isDuo: offer.isDuo,
  }
}
