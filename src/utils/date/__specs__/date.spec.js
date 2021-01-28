import mockdate from 'mockdate'

import { dateStringPlusTimeZone, formatRecommendationDates, formatSearchResultDate } from '../date'

const Jan21 = new Date(2020, 0, 21)
const Feb1 = new Date(2020, 1, 1) // Now
const Feb27_09_09 = new Date(2020, 1, 27, 9, 9)
const Feb27_11_11 = new Date(2020, 1, 27, 11, 11)
const March27 = new Date(2020, 2, 27)
const March28 = new Date(2020, 2, 28, 15, 9)

describe('src | utils | date', () => {
  describe('formatRecommendationDates', () => {
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
        expect(result).toBe('du 25/10/2018 au 26/10/2018')
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
        expect(result).toBe('du 25/10/2018 au 26/10/2018')
      })
    })
  })

  describe('dateStringPlusTimeZone', () => {
    it('should return date string plus the time zone', () => {
      // given
      const dateString = '2019-10-10T20:00:00Z'
      const departementCode = '973'

      // when
      const timestamp = dateStringPlusTimeZone(dateString, departementCode)

      // then
      expect(timestamp).toBe('2019-10-10 17:00:00')
    })
  })

  describe('formatSearchResultDate', () => {
    beforeAll(() => {
      mockdate.set(Feb1)
    })

    it.each`
      what                                            | dates                         | expected
      ${'should handle empty dates'}                  | ${[]}                         | ${null}
      ${'should format a single date <10'}            | ${[Feb27_09_09]}              | ${'Jeudi 27 février 09:09'}
      ${'should format a single date >10'}            | ${[Feb27_11_11]}              | ${'Jeudi 27 février 11:11'}
      ${'should pick first date if both on same day'} | ${[Feb27_09_09, Feb27_11_11]} | ${'Jeudi 27 février 09:09'}
      ${'should pick the first date if many'}         | ${[March27, March28]}         | ${'À partir du 27 mars'}
      ${'should filter past dates - none'}            | ${[Jan21]}                    | ${null}
      ${'should filter past dates - single'}          | ${[Jan21, March28]}           | ${'Samedi 28 mars 15:09'}
      ${'should filter past dates - many'}            | ${[Jan21, March27, March28]}  | ${'À partir du 27 mars'}
    `('$what', ({ dates, expected }) => {
      const timestampsInSeconds = dates && dates.map(date => date.valueOf() / 1000)
      expect(formatSearchResultDate(null, timestampsInSeconds)).toBe(expected)
    })
  })
})
