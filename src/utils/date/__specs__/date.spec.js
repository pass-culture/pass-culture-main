import { formatRecommendationDates, formatEndValidityDate } from '../date'

describe('src | utils | date | date', () => {
  describe('formatEndValidityDate()', () => {
    it('should return formatted date', () => {
      // given
      const date = new Date('2019-09-10T08:05:45.778894Z')

      // when
      const formattedDate = formatEndValidityDate(date)

      // then
      expect(formattedDate).toBe('2020 M09 10')
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
        expect(result).toBe('du 2018-10-25 au 2018-10-26')
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
        expect(result).toBe('du 2018-10-25 au 2018-10-26')
      })
    })
  })
})
