import { DATE } from '../date'

describe('getDatesFromTimeRangeAndDate', () => {
  it('should return dates with beginning and ending times for given date and timerange', () => {
    // Given
    const from_eighteen_to_twenty_two = [18, 22]
    const tuesday_april_28_2020_eleven_thirty_four_am = new Date(2020, 3, 28, 11, 34, 23, 234)

    // When
    const dateWithBeginningAndEndingTimes = DATE.getAllFromTimeRangeAndDate(
      tuesday_april_28_2020_eleven_thirty_four_am,
      from_eighteen_to_twenty_two
    )

    // Then
    const tuesday_april_28_2020_six_pm = new Date(2020, 3, 28, 18, 0, 0, 0)
    const tuesday_april_28_2020_ten_pm = new Date(2020, 3, 28, 22, 0, 0, 0)
    expect(dateWithBeginningAndEndingTimes).toStrictEqual([
      tuesday_april_28_2020_six_pm,
      tuesday_april_28_2020_ten_pm,
    ])
  })

  it('should return dates with beginning and ending times for given date and timerange with extreme values', () => {
    // Given
    const from_midnight_to_twenty_two = [0, 24]
    const tuesday_april_28_2020_eleven_thirty_four_am = new Date(2020, 3, 28, 11, 34, 23, 234)

    // When
    const dateWithBeginningAndEndingTimes = DATE.getAllFromTimeRangeAndDate(
      tuesday_april_28_2020_eleven_thirty_four_am,
      from_midnight_to_twenty_two
    )

    // Then
    const tuesday_april_28_2020_midnight = new Date(2020, 3, 28, 0, 0, 0, 0)
    const wednesday_april_29_2020_midnight = new Date(2020, 3, 29, 0, 0, 0, 0)
    expect(dateWithBeginningAndEndingTimes).toStrictEqual([
      tuesday_april_28_2020_midnight,
      wednesday_april_29_2020_midnight,
    ])
  })
})

describe('getWeekDatesFromDate', () => {
  it('should return dates of the week for a given date', () => {
    // Given
    const monday_april_27_2020_eleven_am = new Date(2020, 3, 27, 11, 0, 0)

    // When
    const dates = DATE.WEEK.getAllFromDate(monday_april_27_2020_eleven_am)

    // Then
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11)
    const wednesday_april_29_2020_eleven_am = new Date(2020, 3, 29, 11)
    const thursday_april_30_2020_eleven_am = new Date(2020, 3, 30, 11)
    const friday_may_01_2020_eleven_am = new Date(2020, 4, 1, 11)
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11)
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11)
    expect(dates).toStrictEqual([
      monday_april_27_2020_eleven_am,
      tuesday_april_28_2020_eleven_am,
      wednesday_april_29_2020_eleven_am,
      thursday_april_30_2020_eleven_am,
      friday_may_01_2020_eleven_am,
      saturday_may_02_2020_eleven_am,
      sunday_may_03_2020_eleven_am,
    ])
  })

  it('should return dates of the week for a given date when in the middle of the week', () => {
    // Given
    const wednesday_april_29_2020_eleven_am = new Date(2020, 3, 29, 11)

    // When
    const dates = DATE.WEEK.getAllFromDate(wednesday_april_29_2020_eleven_am)

    // Then
    const thursday_april_30_2020_eleven_am = new Date(2020, 3, 30, 11)
    const friday_may_01_2020_eleven_am = new Date(2020, 4, 1, 11)
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11)
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11)
    expect(dates).toStrictEqual([
      wednesday_april_29_2020_eleven_am,
      thursday_april_30_2020_eleven_am,
      friday_may_01_2020_eleven_am,
      saturday_may_02_2020_eleven_am,
      sunday_may_03_2020_eleven_am,
    ])
  })

  it('should return date of the week for a given date when date is sunday', () => {
    // Given
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

    // When
    const dates = DATE.WEEK.getAllFromDate(sunday_may_03_2020_eleven_am)

    // Then
    expect(dates).toStrictEqual([sunday_may_03_2020_eleven_am])
  })
})

describe('getWeekEndDatesFromDate', () => {
  it('should return dates of the week end for a given date', () => {
    // Given
    const tuesday_april_28_2020_eleven_am = new Date(2020, 3, 28, 11, 0, 0)

    // When
    const dates = DATE.WEEK_END.getAllFromDate(tuesday_april_28_2020_eleven_am)

    // Then
    const saturday_may_02_2020_eleven_am = new Date(2020, 4, 2, 11)
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11)
    expect(dates).toStrictEqual([saturday_may_02_2020_eleven_am, sunday_may_03_2020_eleven_am])
  })

  it('should return date of the week end for a given date when date is sunday', () => {
    // Given
    const sunday_may_03_2020_eleven_am = new Date(2020, 4, 3, 11, 0, 0)

    // When
    const dates = DATE.WEEK_END.getAllFromDate(sunday_may_03_2020_eleven_am)

    // Then
    expect(dates).toStrictEqual([sunday_may_03_2020_eleven_am])
  })
})
