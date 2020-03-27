import { computeEndValidityDate, dateStringPlusTimeZone, formatRecommendationDates, formatResultDate } from '../date'

describe('src | utils | date', () => {
  describe('computeEndValidityDate', () => {
    it('should return formatted date', () => {
      // given
      const date = new Date('2019-09-10T08:05:45.778894Z')

      // when
      const formattedDate = computeEndValidityDate(date)

      // then
      expect(formattedDate).toBe('10 septembre 2021')
    })
  })

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
        process.env.TZ = 'Europe/Amsterdam'
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
      const departementCode = '97'

      // when
      const timestamp = dateStringPlusTimeZone(dateString, departementCode)

      // then
      expect(timestamp).toBe('2019-10-10 17:00:00')
    })
  })

  describe('formatResultDate', () => {
    it('should null when no dates', () => {
      // given
      const departmentCode = '93'
      const dates = []

      // when
      const result = formatResultDate(departmentCode, dates)

      // then
      expect(result).toBeNull()
    })

    describe('when hours and minutes superior to zero', () => {
      it('should return one date when beginning datetime and end datetime are the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585308698, 1585308699]

        // when
        const result = formatResultDate(departmentCode, dates)

        // then
        expect(result).toBe('ven. 27 mars 11:31')
      })

      it('should return from date when beginning datetime and end datetime are not the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585308698, 1585484866]

        // when
        const result = formatResultDate(departmentCode, dates)

        // then
        expect(result).toBe('A partir du 27 mars')
      })
    })

    describe('when hours and minutes inferior to zero', () => {
      it('should return date when beginning datetime and end datetime are the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585328400, 1585328401]

        // when
        const result = formatResultDate(departmentCode, dates)

        // then
        expect(result).toBe('ven. 27 mars 17:00')
      })

      it('should return date when beginning datetime and end datetime are not the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585414800, 1593018000]

        // when
        const result = formatResultDate(departmentCode, dates)

        // then
        expect(result).toBe('A partir du 28 mars')
      })
    })
  })
})
