import {
  FORMAT_DD_MM_YYYY_HH_mm,
  formatBrowserTimezonedDateAsUTC,
  toDateStrippedOfTimezone,
  toISOStringWithoutMilliseconds,
} from '../date'

describe('formatBrowserTimezonedDateAsUTC', () => {
  it('should format browser date as UTC to ISO by default', () => {
    // given
    const browserTimezonedDate: Date = new Date('2019-02-28T21:59:00')

    // when
    const formattedDate: string =
      formatBrowserTimezonedDateAsUTC(browserTimezonedDate)

    // then
    expect(formattedDate).toBe('2019-02-28T21:59:00Z')
  })

  it('should format browser date as UTC to required format', () => {
    // given
    const browserTimezonedDate: Date = new Date('2019-02-28T21:59:00')

    // when
    const formattedDate: string = formatBrowserTimezonedDateAsUTC(
      browserTimezonedDate,
      FORMAT_DD_MM_YYYY_HH_mm
    )

    // then
    expect(formattedDate).toBe('28/02/2019 21:59')
  })
})

describe('toDateStrippedOfTimezone', () => {
  it('should strip La Réunion timezone', () => {
    // given
    const reunionTimezonedDateIsoString = '2019-02-28T21:59:00+04:00'

    // when
    const date: Date = toDateStrippedOfTimezone(reunionTimezonedDateIsoString)

    // then
    const expectedDate: Date = new Date('2019-02-28T21:59:00')
    expect(date.toISOString()).toBe(expectedDate.toISOString())
  })

  it('should strip Cayenne timezone', () => {
    // given
    const cayenneTimezonedDateIsoString = '2019-02-28T21:59:00-03:00'

    // when
    const date: Date = toDateStrippedOfTimezone(cayenneTimezonedDateIsoString)

    // then
    const expectedDate: Date = new Date('2019-02-28T21:59:00')
    expect(date.toISOString()).toBe(expectedDate.toISOString())
  })
})

describe('toISOStringWithoutMilliseconds', () => {
  it('should return ISO string date without milliseconds', () => {
    // given
    const date: Date = new Date('2020-11-17T08:15:00Z')

    // when
    const dateISOString: string = toISOStringWithoutMilliseconds(date)

    // then
    expect(dateISOString).toBe('2020-11-17T08:15:00Z')
  })
})
