import getHumanizeRelativeDate from '../getHumanizeRelativeDate'
import { formatRecommendationDates } from '../date'

describe('src | utils | date | date', () => {
  describe('getHumanizeRelativeDate()', () => {
    describe('when there is a null date (e.g.: tuto)', () => {
      it('should return null', () => {
        // given
        const offerDate = null

        // when
        const expected = getHumanizeRelativeDate(offerDate)

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when there is a bad date format', () => {
      it('should throw "Date invalide"', () => {
        // given
        const offerDate = 'MEFA'

        // when
        const expected = () => getHumanizeRelativeDate(offerDate)

        // then
        expect(expected).toThrow('Date invalide')
      })
    })

    describe('when the beginning date is not today or tomorrow', () => {
      it('should return null', () => {
        // given
        const offerDate = '2018-07-21T20:00:00Z'

        // when
        const expected = getHumanizeRelativeDate(offerDate)

        // then
        expect(expected).toBeNull()
      })
    })

    describe('when the beginning date is today', () => {
      it('should return "Aujourd’hui"', () => {
        // given
        const offerDate = new Date().toISOString()

        // when
        const expected = getHumanizeRelativeDate(offerDate)

        // then
        expect(expected).toBe('Aujourd’hui')
      })
    })

    describe('when the beginning date is tomorrow', () => {
      it('should return "Demain"', () => {
        // given
        const todayDate = new Date()
        const offerDate = new Date(todayDate)
        const currentDateDay = todayDate.getDate()
        offerDate.setDate(currentDateDay + 1)

        // when
        const expected = getHumanizeRelativeDate(offerDate.toISOString())

        // then
        expect(expected).toBe('Demain')
      })
    })
  })

  describe('formatRecommendationDates()', () => {
    describe('when there is no date given', () => {
      it('should return permanent', () => {
        // given
        const departementCode = '93'
        const dateRange = []

        // when
        const result = formatRecommendationDates(departementCode, dateRange)

        // then
        expect(result).toBe('permanent')
      })
    })

    describe('when there is a date range for Europe/Paris Timezone', () => {
      it('should return the formated date', () => {
        // given
        const departementCode = '93'
        const dateRange = ['2018-10-25T18:00:00Z', '2018-10-26T19:00:00Z']

        // when
        const result = formatRecommendationDates(departementCode, dateRange)

        // then
        // https://github.com/nodejs/node-v0.x-archive/issues/4689
        expect(result).toBe('du Thu 2018-10-25 au Fri 2018-10-26')
      })
    })

    describe('when there is a date range for Cayenne Timezone', () => {
      it('should return the formated date', () => {
        // given
        const departementCode = '97'
        const dateRange = ['2018-10-25T18:00:00Z', '2018-10-26T19:00:00Z']

        // when
        const result = formatRecommendationDates(departementCode, dateRange)

        // then
        // https://github.com/nodejs/node-v0.x-archive/issues/4689
        expect(result).toBe('du Thu 2018-10-25 au Fri 2018-10-26')
      })
    })
  })
})
