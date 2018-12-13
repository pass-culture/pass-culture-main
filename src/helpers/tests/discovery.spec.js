import moment from 'moment'
import { isRecommendationFinished, withRecommandations } from '../discovery'

describe('src | helpers | discovery', () => {
  describe('isRecommendationFinished', () => {
    it('returns false if no offerid', () => {
      const expected = false
      const bookingLimitDatetime = moment().add(1, 'day')
      const recommendation = { offer: { stocks: [{ bookingLimitDatetime }] } }
      const result = isRecommendationFinished(recommendation)
      expect(result).toStrictEqual(expected)
    })
    it('returns false if offerid is tuto', () => {
      const offerid = 'tuto'
      const expected = false
      const bookingLimitDatetime = moment().add(1, 'day')
      const recommendation = { offer: { stocks: [{ bookingLimitDatetime }] } }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
    it('returns false if offerid but no available stocks', () => {
      const offerid = 'AAA'
      const expected = false
      const bookingLimitDatetime = moment().add(1, 'day')
      const recommendation = {
        offer: { stocks: [{ bookingLimitDatetime }, null] },
      }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
    it('return false if recommendation is future', () => {
      const offerid = 'AAA'
      const expected = false
      // tomorrow
      const bookingLimitDatetime = moment().add(1, 'day')
      const recommendation = { offer: { stocks: [{ bookingLimitDatetime }] } }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
    it('return true if recommendation is today', () => {
      const offerid = 'AAA'
      const expected = true
      // today
      const bookingLimitDatetime = moment()
      const recommendation = { offer: { stocks: [{ bookingLimitDatetime }] } }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
    it('return true if recommendation is past', () => {
      const offerid = 'AAA'
      const expected = true
      // yesterday
      const bookingLimitDatetime = moment().subtract(1, 'day')
      const recommendation = { offer: { stocks: [{ bookingLimitDatetime }] } }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
    it('return true if recommendation offer has no booking limit', () => {
      const offerid = 'AAA'
      const expected = true
      const recommendation = { offer: { stocks: [] } }
      const result = isRecommendationFinished(recommendation, offerid)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('withRecommandations', () => {
    // FIXME Negation that return true
    describe('When ???', () => {
      it('should return true', () => {
        const currentRecommendation = {}
        const recommendations = {}
        const previousProps = {
          recommendations: {},
        }
        expect(
          withRecommandations(
            recommendations,
            previousProps,
            currentRecommendation
          )
        ).toEqual(true)
      })
    })
  })
})
