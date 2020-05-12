import { computeTimeRangeFromHoursToSeconds, TIMESTAMP } from '../time'

describe('computeTimeRangeFromHoursToSeconds', () => {
  it('should convert hours in seconds from given time range', () => {
    // When
    const timeRangeInSeconds = computeTimeRangeFromHoursToSeconds([18, 22])

    // Then
    expect(timeRangeInSeconds).toStrictEqual([64800, 79200])
  })
})

describe('getFirstTimestampForGivenDate', () => {
  it('should return the first timestamp of the day', () => {
    // Given
    const april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

    // When
    const result = TIMESTAMP.getFirstOfDate(april_16_2020_two_pm)

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
    const result = TIMESTAMP.getLastOfDate(april_16_2020_two_pm)

    // Then
    const april_16_2020_23_59_59 = 1587081599
    expect(result).toBe(april_16_2020_23_59_59)
  })
})

describe('getTimestampFromDate', () => {
  it('should return the timestamp for a given date', () => {
    // Given
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 0, 0)

    // When
    const result = TIMESTAMP.getFromDate(saturday_may_02_2020_eleven_am)

    // Then
    const saturday_may_02_2020_eleven_am_timestamp = 1588417200
    expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
  })

  it('should return the timestamp for a given date with milliseconds', () => {
    // Given
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 24, 2, 212)

    // When
    const result = TIMESTAMP.getFromDate(saturday_may_02_2020_eleven_am)

    // Then
    const saturday_may_02_2020_eleven_am_timestamp = 1588418643
    expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
  })

  it('should return the timestamp for a given date with milliseconds greater than 500', () => {
    // Given
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 24, 2, 812)

    // When
    const result = TIMESTAMP.getFromDate(saturday_may_02_2020_eleven_am)

    // Then
    const saturday_may_02_2020_eleven_am_timestamp = 1588418643
    expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
  })
})

describe('getBeginningAndEndingTimestampsForGivenTimeRange', () => {
  it('should return timestamps with beginning and ending times for given date and time range', () => {
    // Given
    const from_eighteen_to_twenty_two = [18, 22]
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 34, 23)

    // When
    const dateWithBeginningAndEndingTimes = TIMESTAMP.getAllFromTimeRangeAndDate(
      tuesday_april_28_2020_eleven_am,
      from_eighteen_to_twenty_two
    )

    // Then
    const tuesday_april_28_2020_six_pm_timestamp = 1588096800
    const tuesday_april_28_2020_ten_pm_timestamp = 1588111200

    expect(dateWithBeginningAndEndingTimes).toStrictEqual([
      tuesday_april_28_2020_six_pm_timestamp,
      tuesday_april_28_2020_ten_pm_timestamp,
    ])
  })
})

describe('getLastWeekTimestampFromDate', () => {
  it('should return the last timestamp of the week for a given date', () => {
    // Given
    const thursday_april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

    // When
    const result = TIMESTAMP.WEEK.getLastFromDate(thursday_april_16_2020_two_pm)

    // Then
    const sunday_april_19_2020_23_59_59 = 1587340799
    expect(result).toBe(sunday_april_19_2020_23_59_59)
  })

  it('should return the last timestamp of the week for a given date by changing month', () => {
    // Given
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 0, 0)

    // When
    const result = TIMESTAMP.WEEK.getLastFromDate(tuesday_april_28_2020_eleven_am)

    // Then
    const sunday_may_03_2020_23_59_59 = 1588550399
    expect(result).toBe(sunday_may_03_2020_23_59_59)
  })

  it('should return the last timestamp of the day when sunday', () => {
    // Given
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

    // When
    const result = TIMESTAMP.WEEK.getLastFromDate(sunday_may_03_2020_eleven_am)

    // Then
    const sunday_may_03_2020_23_59_59 = 1588550399
    expect(result).toBe(sunday_may_03_2020_23_59_59)
  })
})

describe('getWeekTimestampsFromTimeRangeAndDate', () => {
  it('should return dates of the week with beginning and ending times for given date and timerange', () => {
    // Given
    const from_eighteen_to_twenty_two = [18, 22]
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 34, 23)

    // When
    const dateWithBeginningAndEndingTimes = TIMESTAMP.WEEK.getAllFromTimeRangeAndDate(
      tuesday_april_28_2020_eleven_am,
      from_eighteen_to_twenty_two
    )

    // Then
    const april_28_2020_six_pm_timestamp = 1588096800
    const april_28_2020_ten_pm_timestamp = 1588111200
    const april_29_2020_six_pm_timestamp = 1588183200
    const april_29_2020_ten_pm_timestamp = 1588197600
    const april_30_2020_six_pm_timestamp = 1588269600
    const april_30_2020_ten_pm_timestamp = 1588284000
    const may_01_2020_six_pm_timestamp = 1588356000
    const may_01_2020_ten_pm_timestamp = 1588370400
    const may_02_2020_six_pm_timestamp = 1588442400
    const may_02_2020_ten_pm_timestamp = 1588456800
    const may_03_2020_six_pm_timestamp = 1588528800
    const may_03_2020_ten_pm_timestamp = 1588543200
    expect(dateWithBeginningAndEndingTimes).toStrictEqual([
      [april_28_2020_six_pm_timestamp, april_28_2020_ten_pm_timestamp],
      [april_29_2020_six_pm_timestamp, april_29_2020_ten_pm_timestamp],
      [april_30_2020_six_pm_timestamp, april_30_2020_ten_pm_timestamp],
      [may_01_2020_six_pm_timestamp, may_01_2020_ten_pm_timestamp],
      [may_02_2020_six_pm_timestamp, may_02_2020_ten_pm_timestamp],
      [may_03_2020_six_pm_timestamp, may_03_2020_ten_pm_timestamp],
    ])
  })
})

describe('getFirstWeekEndTimestampFromDate', () => {
  it('should return the first timestamp of the weekend for a given date', () => {
    // Given
    const thursday_april_16_2020_two_pm = new Date(2020, 3, 16, 14, 0, 0)

    // When
    const result = TIMESTAMP.WEEK_END.getFirstFromDate(thursday_april_16_2020_two_pm)

    // Then
    const saturday_april_18_2020_midnight = 1587168000
    expect(result).toBe(saturday_april_18_2020_midnight)
  })

  it('should return the first timestamp of the weekend for a given date by changing month', () => {
    // Given
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 0, 0)

    // When
    const result = TIMESTAMP.WEEK_END.getFirstFromDate(tuesday_april_28_2020_eleven_am)

    // Then
    const saturday_may_02_2020_midnight = 1588377600
    expect(result).toBe(saturday_may_02_2020_midnight)
  })

  it('should return current timestamp when saturday', () => {
    // Given
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11, 0, 0)

    // When
    const result = TIMESTAMP.WEEK_END.getFirstFromDate(saturday_may_02_2020_eleven_am)

    // Then
    const saturday_may_02_2020_eleven_am_timestamp = 1588417200
    expect(result).toBe(saturday_may_02_2020_eleven_am_timestamp)
  })

  it('should return current timestamp when sunday', () => {
    // Given
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

    // When
    const result = TIMESTAMP.WEEK_END.getFirstFromDate(sunday_may_03_2020_eleven_am)

    // Then
    const sunday_may_03_2020_eleven_am_timestamp = 1588503600
    expect(result).toBe(sunday_may_03_2020_eleven_am_timestamp)
  })

  it('should return current timestamp when sunday with milliseconds', () => {
    // Given
    const sunday_may_03_2020_eleven_am_with_milliseconds = new Date(2020, 4, 3, 11, 3, 26, 213)

    // When
    const result = TIMESTAMP.WEEK_END.getFirstFromDate(
      sunday_may_03_2020_eleven_am_with_milliseconds
    )

    // Then
    const sunday_may_03_2020_eleven_am_timestamp_ceiled = 1588503807
    expect(result).toBe(sunday_may_03_2020_eleven_am_timestamp_ceiled)
  })
})

describe('getWeekEndTimestampsFromTimeRangeAndDate', () => {
  it('should return dates with beginning and ending times for given date and timerange', () => {
    // Given
    const from_eighteen_to_twenty_two = [18, 22]
    const tuesday_april_28_2020_eleven_thirty_four_am = new Date(2020, 3, 28, 11, 34, 23)

    // When
    const dateWithBeginningAndEndingTimes = TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate(
      tuesday_april_28_2020_eleven_thirty_four_am,
      from_eighteen_to_twenty_two
    )

    // Then
    const may_02_2020_six_pm_timestamp = 1588442400
    const may_02_2020_ten_pm_timestamp = 1588456800
    const may_03_2020_six_pm_timestamp = 1588528800
    const may_03_2020_ten_pm_timestamp = 1588543200
    expect(dateWithBeginningAndEndingTimes).toStrictEqual([
      [may_02_2020_six_pm_timestamp, may_02_2020_ten_pm_timestamp],
      [may_03_2020_six_pm_timestamp, may_03_2020_ten_pm_timestamp],
    ])
  })
})
