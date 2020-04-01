import {
  computeEndValidityDate,
  dateStringPlusTimeZone,
  formatRecommendationDates,
  formatSearchResultDate,
} from '../date'

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

  describe('formatSearchResultDate', () => {
    it('should return null when no dates', () => {
      // given
      const departmentCode = '93'
      const dates = []

      // when
      const result = formatSearchResultDate(departmentCode, dates)

      // then
      expect(result).toBeNull()
    })

    describe('when hours and minutes superior to 10', () => {
      it('should return one date when beginning datetime and end datetime are the same day', () => {
        // given
        const departmentCode = null
        const dates = [1582801860, 1582805340]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('Jeudi 27 février 11:11')
      })

      it('should return date when there is only one date', () => {
        // given
        const departmentCode = null
        const dates = [1582801860]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('Jeudi 27 février 11:11')
      })

      it('should indicate beginning datetime as starting date when beginning datetime and end datetime are not the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585308698, 1585484866]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('A partir du 27 mars')
      })
    })

    describe('when hours and minutes inferior to 10', () => {
      it('should return date when beginning datetime and end datetime are the same day', () => {
        // given
        const departmentCode = null
        const dates = [1582794540, 1582805340]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('Jeudi 27 février 09:09')
      })

      it('should return date when there is only one date', () => {
        // given
        const departmentCode = null
        const dates = [1582794540]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('Jeudi 27 février 09:09')
      })

      it('should indicate beginning datetime as starting date when beginning datetime and end datetime are not the same day', () => {
        // given
        const departmentCode = null
        const dates = [1585414800, 1593018000]

        // when
        const result = formatSearchResultDate(departmentCode, dates)

        // then
        expect(result).toBe('A partir du 28 mars')
      })
    })
  })
})
