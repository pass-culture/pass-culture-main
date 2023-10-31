import { Offer } from 'core/Offers/types'
import { individualOfferFactory } from 'screens/Offers/utils/individualOffersFactories'

import { offerHasBookingQuantity } from '../offerHasBookingQuantity'

describe('offerHasBookingQuantity', () => {
  let offers: Offer[] = []
  let stock
  beforeEach(() => {
    const offer = individualOfferFactory()
    const stockFactories = {
      remainingQuantity: 0,
    }
    stock = stockFactories
    offers = [
      { ...offer, stocks: [stock] },
      { ...offer, stocks: [stock] },
    ]
  })

  it('should return true when one of the offers has a bookingQuantity', () => {
    offers[0].stocks[0].bookingQuantity = 2
    const hasBookingQuantity = offerHasBookingQuantity(offers)
    expect(hasBookingQuantity).toBeTruthy()
  })

  it('should return false when offers has no bookingQuantity in any stock', () => {
    const hasBookingQuantity = offerHasBookingQuantity(offers)
    expect(hasBookingQuantity).toBeFalsy()
  })
})
