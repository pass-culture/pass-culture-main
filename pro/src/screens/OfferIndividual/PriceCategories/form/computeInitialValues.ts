import { IOfferIndividual } from 'core/Offers/types'

import { FIRST_INITIAL_PRICE_CATEGORY } from './constants'
import { PriceCategoriesFormValues } from './types'

export const computeInitialValues = (
  offer: IOfferIndividual
): PriceCategoriesFormValues => {
  return {
    priceCategories: [FIRST_INITIAL_PRICE_CATEGORY],
    isDuo: offer.isDuo,
  }
}
