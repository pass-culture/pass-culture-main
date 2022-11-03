import { MAX_OFFERS_TO_DISPLAY } from 'core/Offers/constants'

export const getOffersCountToDisplay = offersCount =>
  offersCount <= MAX_OFFERS_TO_DISPLAY ? offersCount.toString() : '500+'
