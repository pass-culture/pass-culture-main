import mockdate from 'mockdate'

import { dateStringPlusTimeZone, formatRecommendationDates, formatSearchResultDate } from '../date'

// TZ is mocked as UTC. We use UTC+1 (Europe/Paris). Thus we set the date to date-1
const Jan21 = new Date(2020, 0, 21)
const Feb1 = new Date(2020, 1, 1) // Now
const Feb27_09_09 = new Date(2020, 1, 27, 8, 9)
const Feb27_11_11 = new Date(2020, 1, 27, 10, 11)
const March27 = new Date(2020, 2, 27)
const March28 = new Date(2020, 2, 28, 14, 9)

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
      what                                                                         | dates                         | expected
      ${'should handle empty dates'}                                               | ${[]}                         | ${null}
      ${'should show date and hour with correct format'}                           | ${[Feb27_11_11]}              | ${'Jeudi 27 février 11:11'}
      ${'should pad hours and minutes with 0'}                                     | ${[Feb27_09_09]}              | ${'Jeudi 27 février 09:09'}
      ${'should show earliest date and hour when both dates are on the same day'}  | ${[Feb27_09_09, Feb27_11_11]} | ${'Jeudi 27 février 09:09'}
      ${'should sort the available dates and pick the earliest'}                   | ${[March28, March27]}         | ${'À partir du 27 mars'}
      ${'should not show any dates if all dates are in the past'}                  | ${[Jan21]}                    | ${null}
      ${'should show the only date not in the past'}                               | ${[Jan21, March28]}           | ${'Samedi 28 mars 15:09'}
      ${'should show the period beginning with the earliest date not in the past'} | ${[Jan21, March27, March28]}  | ${'À partir du 27 mars'}
    `('$what', ({ dates, expected }) => {
      const timestampsInSeconds = dates.map(date => date.valueOf() / 1000)
      expect(formatSearchResultDate(null, timestampsInSeconds)).toBe(expected)
    })

    it('should format correctly according to department code', () => {
      const Feb23_21 = new Date(2020, 1, 23, 21, 9).valueOf() / 1000
      // null: Europe/Paris by default
      expect(formatSearchResultDate(null, [Feb23_21])).toBe('Dimanche 23 février 22:09')

      // Europe/Paris - UTC+1
      expect(formatSearchResultDate('75', [Feb23_21])).toBe('Dimanche 23 février 22:09')

      // America/Cayenne - UTC-3
      expect(formatSearchResultDate('973', [Feb23_21])).toBe('Dimanche 23 février 18:09')

      // Indian/Reunion - UTC+4
      expect(formatSearchResultDate('974', [Feb23_21])).toBe('Lundi 24 février 01:09')
    })
  })
})
