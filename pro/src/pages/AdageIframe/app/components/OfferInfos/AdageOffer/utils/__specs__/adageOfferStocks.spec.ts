import { defaultCollectiveOffer } from '@/commons/utils/factories/adageFactories'

import { getBookableOfferStockPrice } from '../adageOfferStocks'

describe('adageOfferStocks', () => {
  describe('getBookableOfferStockPrice', () => {
    it('should return the offer price and number of students', () => {
      const stockText = getBookableOfferStockPrice({
        ...defaultCollectiveOffer,
        stock: {
          id: 1,
          price: 100,
          numberOfTickets: 20,
        },
      })

      expect(stockText).toEqual('1\xa0€ pour 20 participants')
    })
  })
})
