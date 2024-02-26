import {
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { venueFactory } from 'pages/CollectiveOffers/utils/collectiveOffersFactories'

let offerId = 1
let stockId = 1

export const listOffersStockFactory = (
  customListOffersStockFactory: Partial<ListOffersStockResponseModel> = {}
): ListOffersStockResponseModel => {
  const currentStockId = stockId++
  return {
    id: currentStockId,
    hasBookingLimitDatetimePassed: false,
    remainingQuantity: 100,
    ...customListOffersStockFactory,
  }
}

export const individualOfferFactory = (
  customOffer: Partial<ListOffersOfferResponseModel> = {}
): ListOffersOfferResponseModel => {
  const currentOfferId = offerId++

  return {
    id: currentOfferId,
    status: OfferStatus.ACTIVE,
    subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: false,
    name: `offer name ${offerId}`,
    isEvent: true,
    isThing: false,
    venue: venueFactory(),
    stocks: [],
    isEditable: true,
    ...customOffer,
  }
}
