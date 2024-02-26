import { ListOffersStockResponseModel, OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
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

export const individualOfferFactory = (customOffer = {}): Offer => {
  const currentOfferId = offerId++
  return {
    id: currentOfferId,
    status: OfferStatus.ACTIVE,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: false,
    name: `offer name ${offerId}`,
    isEvent: true,
    venue: venueFactory(),
    stocks: [],
    isEditable: true,
    ...customOffer,
  }
}
