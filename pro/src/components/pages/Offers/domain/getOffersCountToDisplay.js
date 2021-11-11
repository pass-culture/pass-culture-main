import { MAX_OFFERS_TO_DISPLAY } from 'components/pages/Offers/Offers/_constants'

export const getOffersCountToDisplay = offersCount =>
  offersCount <= MAX_OFFERS_TO_DISPLAY ? offersCount.toString() : '200+'
