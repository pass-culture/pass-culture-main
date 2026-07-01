import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
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
          servicePrice: 100,
          collectiveAdditionalFees: [],
          numberOfTickets: 20,
        },
      })

      expect(stockText).toEqual('1\xa0€ pour 20 participants')
    })

    describe('WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS', () => {
      it('should include numberOfTeachers in the total participants count', () => {
        const stockText = getBookableOfferStockPrice(
          {
            ...defaultCollectiveOffer,
            stock: {
              id: 1,
              price: 14500,
              servicePrice: 10000,
              collectiveAdditionalFees: [
                { type: CollectiveAdditionalFeeType.TRAVEL, amount: 4500 },
              ],
              numberOfTickets: 28,
              numberOfTeachers: 2,
            },
          },
          true
        )

        expect(stockText).toEqual('145\xa0€ pour 30 participants')
      })

      it('should handle numberOfTeachers = 0', () => {
        const stockText = getBookableOfferStockPrice(
          {
            ...defaultCollectiveOffer,
            stock: {
              id: 1,
              price: 10000,
              servicePrice: 10000,
              collectiveAdditionalFees: [],
              numberOfTickets: 10,
              numberOfTeachers: 0,
            },
          },
          true
        )

        expect(stockText).toEqual('100\xa0€ pour 10 participants')
      })
    })
  })
})
