import { selectIsEnoughStockForOfferDuo } from '../stocksSelector'

describe('src | components | layout | Duo | selectors | stocksSelector', () => {
  describe('selectIsEnoughStockForOfferDuo', () => {
    it('should return true when there is stock with more than two available', () => {
      // given
      const state = {
        data: {
          stocks: [
            {
              offerId: 'AAAA',
              available: 2,
            },
          ],
        },
      }

      const offerId = 'AAAA'

      // when
      const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

      // then
      expect(isEnoughStockForOfferDuo).toBe(true)
    })

    it('should return false when there is no stock with more than two available', () => {
      // given
      const state = {
        data: {
          stocks: [
            {
              offerId: 'AAAA',
              available: 1,
            },
          ],
        },
      }

      const offerId = 'AAAA'

      // when
      const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

      // then
      expect(isEnoughStockForOfferDuo).toBe(false)
    })

    it('should return false when there is no match between stock and offer', () => {
      // given
      const state = {
        data: {
          stocks: [
            {
              offerId: 'AAAA',
              available: 5,
            },
          ],
        },
      }

      const offerId = 'BBBB'

      // when
      const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

      // then
      expect(isEnoughStockForOfferDuo).toBe(false)
    })
  })
})
