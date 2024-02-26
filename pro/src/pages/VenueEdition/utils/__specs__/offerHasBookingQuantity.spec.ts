import { Offer } from 'core/Offers/types'
import {
  individualOfferFactory,
  listOffersStockFactory,
} from 'screens/Offers/utils/individualOffersFactories'

import { offerHasBookingQuantity } from '../offerHasBookingQuantity'

describe('offerHasBookingQuantity', () => {
  let offers: Offer[] = []
  beforeEach(() => {
    const offer = individualOfferFactory()
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
