import {
  FORMAT_DD_MM_YYYY_HH_mm,
  formatBrowserTimezonedDateAsUTC,
  toDateStrippedOfTimezone,
  toISOStringWithoutMilliseconds,
} from '../date'

describe('formatBrowserTimezonedDateAsUTC', () => {
  it('should format browser date as UTC to ISO by default', () => {
    const browserTimezonedDate = new Date('2019-02-28T21:59:00')

    const formattedDate = formatBrowserTimezonedDateAsUTC(browserTimezonedDate)

    expect(formattedDate).toBe('2019-02-28T21:59:00Z')
  })

  it('should format browser date as UTC to required format', () => {
    const browserTimezonedDate = new Date('2019-02-28T21:59:00')

    const formattedDate = formatBrowserTimezonedDateAsUTC(
      browserTimezonedDate,
      FORMAT_DD_MM_YYYY_HH_mm
    )

    expect(formattedDate).toBe('28/02/2019 21:59')
  })
})

describe('toDateStrippedOfTimezone', () => {
  it('should strip La Réunion timezone', () => {
    const cayenneTimezonedDateIsoString = '2019-02-28T21:59:00+04:00'

    const date = toDateStrippedOfTimezone(cayenneTimezonedDateIsoString)

    const expectedDate = new Date('2019-02-28T21:59:00')
    expect(date.toISOString()).toBe(expectedDate.toISOString())
  })

  it('should strip Cayenne timezone', () => {
    const cayenneTimezonedDateIsoString = '2019-02-28T21:59:00-03:00'

    const date = toDateStrippedOfTimezone(cayenneTimezonedDateIsoString)

    const expectedDate = new Date('2019-02-28T21:59:00')
    expect(date.toISOString()).toBe(expectedDate.toISOString())
  })
})

describe('toISOStringWithoutMilliseconds', () => {
  it('should return ISO string date without milliseconds', () => {
    const date = new Date('2020-11-17T08:15:00Z')

    const dateISOString = toISOStringWithoutMilliseconds(date)

    expect(dateISOString).toBe('2020-11-17T08:15:00Z')
  })
})
