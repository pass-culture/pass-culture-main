import {
  computeEndValidityDate,
  dateStringPlusTimeZone,
  formatRecommendationDates,
  formatSearchResultDate,
  getFirstTimestampForGivenDate,
  getFirstTimestampOfTheWeekEndForGivenDate,
  getLastTimestampForGivenDate,
  getLastTimestampOfTheWeekForGivenDate,
  getTimestampFromDate,
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
      const departementCode = '973'

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

  describe('getFirstTimestampForGivenDate', () => {
    it('should return the first timestamp of the day', () => {
      // Given
      const april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

      // When
      const result = getFirstTimestampForGivenDate(april_16_2020_two_pm)

      // Then
      const april_16_2020_midnight = 1586995200
      expect(result).toBe(april_16_2020_midnight)
    })
  })

  describe('getLastTimestampForGivenDate', () => {
    it('should return the last timestamp of the day', () => {
      // Given
      const april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

      // When
      const result = getLastTimestampForGivenDate(april_16_2020_two_pm)

      // Then
      const april_16_2020_23_59_59 = 1587081599
      expect(result).toBe(april_16_2020_23_59_59)
    })
  })

  describe('getLastTimestampOfTheWeekForGivenDate', () => {
    it('should return the last timestamp of the week for a given date', () => {
      // Given
      const thursday_april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

      // When
      const result = getLastTimestampOfTheWeekForGivenDate(thursday_april_16_2020_two_pm)

      // Then
      const sunday_april_19_2020_23_59_59 = 1587340799
      expect(result).toBe(sunday_april_19_2020_23_59_59)
    })

    it('should return the last timestamp of the week for a given date by changing month', () => {
      // Given
      const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 0, 0)

      // When
      const result = getLastTimestampOfTheWeekForGivenDate(tuesday_april_28_2020_eleven_am)

      // Then
      const sunday_may_03_2020_23_59_59 = 1588550399
      expect(result).toBe(sunday_may_03_2020_23_59_59)
    })

    it('should return the last timestamp of the day when sunday', () => {
      // Given
      const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

      // When
      const result = getLastTimestampOfTheWeekForGivenDate(sunday_may_03_2020_eleven_am)

      // Then
      const sunday_may_03_2020_23_59_59 = 1588550399
      expect(result).toBe(sunday_may_03_2020_23_59_59)
    })
  })

  describe('getFirstTimestampOfTheWeekEndForGivenDate', () => {
    it('should return the first timestamp of the weekend for a given date', () => {
      // Given
      const thursday_april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

      // When
      const result = getFirstTimestampOfTheWeekEndForGivenDate(thursday_april_16_2020_two_pm)

      // Then
      const saturday_april_18_2020_midnight = 1587168000
      expect(result).toBe(saturday_april_18_2020_midnight)
    })

    it('should return the first timestamp of the weekend for a given date by changing month', () => {
      // Given
      const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 0, 0)

      // When
      const result = getFirstTimestampOfTheWeekEndForGivenDate(tuesday_april_28_2020_eleven_am)

      // Then
      const saturday_may_02_2020_midnight = 1588377600
      expect(result).toBe(saturday_may_02_2020_midnight)
    })

    it('should return current timestamp when saturday', () => {
      // Given
      const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 0, 0)

      // When
      const result = getFirstTimestampOfTheWeekEndForGivenDate(saturday_may_02_2020_eleven_am)

      // Then
      const saturday_may_02_2020_eleven_am_timestamp = 1588417200
      expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
    })

    it('should return current timestamp when sunday', () => {
      // Given
      const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

      // When
      const result = getFirstTimestampOfTheWeekEndForGivenDate(sunday_may_03_2020_eleven_am)

      // Then
      const sunday_may_03_2020_eleven_am_timestamp = 1588503600
      expect(result).toBe(sunday_may_03_2020_eleven_am_timestamp)
    })

    it('should return current timestamp when sunday with milliseconds', () => {
      // Given
      const sunday_may_03_2020_eleven_am_with_milliseconds = new Date(2020, 4, 3, 11, 3, 26, 213)

      // When
      const result = getFirstTimestampOfTheWeekEndForGivenDate(
        sunday_may_03_2020_eleven_am_with_milliseconds
      )

      // Then
      const sunday_may_03_2020_eleven_am_timestamp_ceiled = 1588503807
      expect(result).toBe(sunday_may_03_2020_eleven_am_timestamp_ceiled)
    })
  })

  describe('getTimestampFromDate', () => {
    it('should return the timestamp for a given date', () => {
      // Given
      const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 0, 0)

      // When
      const result = getTimestampFromDate(saturday_may_02_2020_eleven_am)

      // Then
      const saturday_may_02_2020_eleven_am_timestamp = 1588417200
      expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
    })

    it('should return the timestamp for a given date with milliseconds', () => {
      // Given
      const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 24, 2, 212)

      // When
      const result = getTimestampFromDate(saturday_may_02_2020_eleven_am)

      // Then
      const saturday_may_02_2020_eleven_am_timestamp = 1588418643
      expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
    })

    it('should return the timestamp for a given date with milliseconds greater than 500', () => {
      // Given
      const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 24, 2, 812)

      // When
      const result = getTimestampFromDate(saturday_may_02_2020_eleven_am)

      // Then
      const saturday_may_02_2020_eleven_am_timestamp = 1588418643
      expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
    })
  })
})
