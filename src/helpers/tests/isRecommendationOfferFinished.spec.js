import { isRecommendationOfferFinished } from '../isRecommendationOfferFinished'

describe('src | helpers | isRecommendationOfferFinished', () => {
  describe('isRecommendationOfferFinished', () => {
    it('should return false when no recommendation', () => {
      // when
      const result = isRecommendationOfferFinished(null)

      // then
      expect(result).toBe(false)
    })

    it('should return false when no offerId', () => {
      // given
      const recommendation = { offer: {} }

      // when
      const result = isRecommendationOfferFinished(recommendation)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offerId is tuto', () => {
      // given
      const offerId = 'tuto'
      const recommendation = { offer: {} }

      // when
      const result = isRecommendationOfferFinished(recommendation, offerId)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offer is not finished', () => {
      // given
      const offerId = 'AAA'
      const recommendation = {
        offer: {
          isFinished: false,
        },
      }

      // when
      const result = isRecommendationOfferFinished(recommendation, offerId)

      // then
      expect(result).toBe(false)
    })

    it('should return true when offer is finished', () => {
      // given
      const offerId = 'AAA'
      const recommendation = {
        offer: {
          isFinished: true,
        },
      }

      // when
      const result = isRecommendationOfferFinished(recommendation, offerId)

      // then
      expect(result).toBe(true)
    })
  })
})
