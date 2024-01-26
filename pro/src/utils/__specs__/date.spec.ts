import {
  FORMAT_DD_MM_YYYY_HH_mm,
  formatBrowserTimezonedDateAsUTC,
  formatShortDateForInput,
  formatTimeForInput,
  getRangeToFrenchText,
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

describe('getRangeToFrenchText', () => {
  it('should display only one day when the starting date and ending date are the same day', () => {
    const from = new Date('2020-11-17T08:15:00Z')
    const to = new Date('2020-11-17T23:59:00Z')

    const formattedRange = getRangeToFrenchText(from, to)

    expect(formattedRange).toBe('Le mardi 17 novembre 2020 à 08h15')
  })

  it('should format the months for both dates when the starting date and ending date are the same year', () => {
    const from = new Date('2020-11-17T08:15:00Z')
    const to = new Date('2020-12-10T23:59:00Z')

    const formattedRange = getRangeToFrenchText(from, to)

    expect(formattedRange).toBe('Du 17 novembre au 10 décembre 2020 à 08h15')
  })

  it('should format the months and years for both dates when the starting date and ending date are on different years', () => {
    const from = new Date('2020-11-17T08:15:00Z')
    const to = new Date('2021-01-10T23:59:00Z')

    const formattedRange = getRangeToFrenchText(from, to)

    expect(formattedRange).toBe(
      'Du 17 novembre 2020 au 10 janvier 2021 à 08h15'
    )
  })

  it('should not display the time when the starting date is at midnight', () => {
    const from = new Date('2020-11-17T00:00:00Z')
    const to = new Date('2021-01-10T23:59:00Z')

    const formattedRange = getRangeToFrenchText(from, to)

    expect(formattedRange).toBe('Du 17 novembre 2020 au 10 janvier 2021')
  })

  it('should not display the time minutes when the starting date minutes are 00', () => {
    const from = new Date('2020-11-17T08:00:00Z')
    const to = new Date('2021-01-10T23:59:00Z')

    const formattedRange = getRangeToFrenchText(from, to)

    expect(formattedRange).toBe('Du 17 novembre 2020 au 10 janvier 2021 à 08h')
  })

  it('should format a date with the right format for a HTML input', () => {
    const date = new Date('2020-11-17T08:00:00Z')

    expect(formatShortDateForInput(date)).toBe('2020-11-17')
  })

  it('should format a time with the right format for a HTML input', () => {
    const date = new Date('2020-11-17T23:10:00Z')

    expect(formatTimeForInput(date)).toBe('23:10')
  })
})
