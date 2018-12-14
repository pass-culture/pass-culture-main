import moment from 'moment'
import { isRecommendationFinished, isRecommendations } from '../discovery'

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

  describe('isRecommendations', () => {
    const withRecommendations = [
      {
        bookingsIds: [],
        dateCreated: '2018-12-13T10:38:28.715863Z',
        dateRead: null,
        dateUpdated: '2018-12-13T10:38:28.715882Z',
        distance: '13 km',
        firstThumbDominantColor: [0, 0, 0],
        id: 'AHZQ',
        index: 0,
        inviteforEventOccurrenceId: null,
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediation: {
          authorId: null,
          backText: 'Some back test',
          credit: null,
          dateCreated: '2018-12-05T12:51:00.737598Z',
          dateModifiedAtLastProvider: '2018-12-05T12:51:13.490793Z',
        },
        mediationId: 'V9',
        modelName: 'Recommendation',
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2018-12-05T12:51:00.737510Z',
          dateModifiedAtLastProvider: '2018-12-05T12:51:08.764725Z',
          dateRange: Array(2),
          eventId: 'CA',
        },
        offerId: '54',
        search: null,
        shareMedium: null,
        thumbUrl: 'http://localhost/storage/thumbs/mediations/V9',
        tz: 'Europe/Paris',
        uniqId: 'event_CA',
        userId: 'DY',
        validUntilDate: '2018-12-16T10:38:28.725070Z',
      },
    ]
    describe('When there is recommendations availables', () => {
      it('should return true', () => {
        const currentRecommendation = {}
        const previousProps = {}

        expect(
          isRecommendations(
            withRecommendations,
            previousProps,
            currentRecommendation
          )
        ).toEqual(true)
      })
    })
    describe.skip('When there is no recommendations and no previous recommendations availables', () => {
      it('should return false', () => {
        const emptyRecommendations = []
        const previousProps = {
          recommendations: undefined,
        }
        // si recommendations = [] le !recommendations renvoie false, si undefined, renvoie true...
        expect(isRecommendations(emptyRecommendations, previousProps)).toEqual(
          false
        )
      })
    })
  })
  describe('isNewRecommendations', () => {})
  describe('isCurrentRecommandation', () => {})
  describe('isNewCurrentRecommandation', () => {})
})
