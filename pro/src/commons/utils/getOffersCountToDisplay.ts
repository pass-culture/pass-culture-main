import { MAX_OFFERS_TO_DISPLAY } from '@/commons/core/Offers/constants'
export const getOffersCountToDisplay = (offersCount: number) =>
  offersCount < MAX_OFFERS_TO_DISPLAY
    ? offersCount.toString()
    : `${MAX_OFFERS_TO_DISPLAY}+`
