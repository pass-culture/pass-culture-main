import { ListOffersOfferResponseModel } from 'apiClient/v1'
import {
  listOffersStockFactory,
  listOffersOfferFactory,
} from 'utils/individualApiFactories'

import { offerHasBookingQuantity } from '../offerHasBookingQuantity'

describe('offerHasBookingQuantity', () => {
  let offers: ListOffersOfferResponseModel[] = []

  beforeEach(() => {
    const offer = listOffersOfferFactory()
    offers = [
      { ...offer, stocks: [listOffersStockFactory({ remainingQuantity: 0 })] },
      { ...offer, stocks: [listOffersStockFactory({ remainingQuantity: 0 })] },
    ]
  })

  it('should return true when one of the offers has a bookingQuantity', () => {
    offers[0].stocks[0] = listOffersStockFactory({
      remainingQuantity: 0,
      bookingQuantity: 2,
    })
    const hasBookingQuantity = offerHasBookingQuantity(offers)
    expect(hasBookingQuantity).toBeTruthy()
  })

  it('should return false when offers has no bookingQuantity in any stock', () => {
    const hasBookingQuantity = offerHasBookingQuantity(offers)
    expect(hasBookingQuantity).toBeFalsy()
  })
})
