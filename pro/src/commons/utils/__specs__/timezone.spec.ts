import {
  convertTimeFromVenueTimezoneToUtc,
  formatLocalTimeDateString,
  getDepartmentTimezone,
  isValidTime,
} from '../timezone'

describe('isValidTime', () => {
  it('should return true for a valid time', () => {
    const time = '12:00'
    const toBePaddedTime = '9:00'
    expect(isValidTime(time)).toBe(true)
    expect(isValidTime(toBePaddedTime)).toBe(true)
  })

  it('should return false for an invalid time', () => {
    const undefinedTime = undefined
    const randomStringTime = ''
    const outOfBoundTime = '24:00'
    expect(isValidTime(undefinedTime)).toBe(false)
    expect(isValidTime(randomStringTime)).toBe(false)
    expect(isValidTime(outOfBoundTime)).toBe(false)
  })
})

describe('formatLocalTimeDateString', () => {
  it('should return a formatted date with Paris departement code and specified format', () => {
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '75'
    const dateFormat = 'EEEE d MMMM yyyy, HH:mm'

    const formattedDate = formatLocalTimeDateString(
      date,
      departementCode,
      dateFormat
    )

    expect(formattedDate).toBe('jeudi 28 février 2019, 22:59')
  })

  it('should return a formatted date with Cayenne departement code and specified format', () => {
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '973'
    const dateFormat = 'EEEE d MMMM yyyy, HH:mm'

    const formattedDate = formatLocalTimeDateString(
      date,
      departementCode,
      dateFormat
    )

    expect(formattedDate).toBe('jeudi 28 février 2019, 18:59')
  })

  it('should return a formatted date with Reunion departement code and default format', () => {
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '974'

    const formattedDate = formatLocalTimeDateString(date, departementCode)

    expect(formattedDate).toBe('vendredi 01/03/2019 à 01:59')
  })
})

describe('getDepartmentTimezone', () => {
  it('should return Paris timezone for Paris', () => {
    const departementCode = '75'

    const timezone = getDepartmentTimezone(departementCode)

    expect(timezone).toBe('Europe/Paris')
  })

  it('should return Cayenne timezone for 973', () => {
    const departementCode = '973'

    const timezone = getDepartmentTimezone(departementCode)

    expect(timezone).toBe('America/Cayenne')
  })

  it('should return Reunion timezone for 974', () => {
    const departementCode = '974'

    const timezone = getDepartmentTimezone(departementCode)

    expect(timezone).toBe('Indian/Reunion')
  })
})

// I don't find a way to change the timezone used in the test
// so the test is incomplete
// if it was possible we would have prefered to test with TZ=Europe/Paris, TZ=America/Cayenne, etc.
describe('convertFromLocalTimeToVenueTimezoneInUtc', () => {
  it('should convert from my locale to departement timezone and give result in utc', () => {
    // Fix the date to avoid the test failing when changing from CET to CEST for Paris
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2024-01-01'))

    const timeInVersailles = convertTimeFromVenueTimezoneToUtc('12:00', '78')
    const timeInTahiti = convertTimeFromVenueTimezoneToUtc('12:00', '987')
    const timeInGuadeloupe = convertTimeFromVenueTimezoneToUtc('12:00', '971')

    expect(timeInVersailles).toBe('11:00')
    expect(timeInTahiti).toBe('22:00')
    expect(timeInGuadeloupe).toBe('16:00')

    vi.useRealTimers()
  })

  it('should convert from my locale to departement timezone and give result in utc with a different local time', () => {
    //  We change the reference date of the test to make sure it does not influence the time conversion
    const timezoneOffsetDate = new Date('2024-01-01')
    timezoneOffsetDate.setHours(timezoneOffsetDate.getHours() - 2)
    vi.useFakeTimers()
    vi.setSystemTime(timezoneOffsetDate)

    const timeInVersailles = convertTimeFromVenueTimezoneToUtc('12:00', '78')
    const timeInTahiti = convertTimeFromVenueTimezoneToUtc('12:00', '987')
    const timeInGuadeloupe = convertTimeFromVenueTimezoneToUtc('12:00', '971')

    expect(timeInVersailles).toBe('11:00')
    expect(timeInTahiti).toBe('22:00')
    expect(timeInGuadeloupe).toBe('16:00')

    vi.useRealTimers()
  })
})
