import { toBookingLimitDatetime } from '../toBookingLimitDatetime'

describe('toBookingLimitDatetime', () => {
  const departementCode = '75'

  it('should return null for invalid input', () => {
    expect(toBookingLimitDatetime('', departementCode)).toBeNull()
    expect(toBookingLimitDatetime(undefined, departementCode)).toBeNull()
    expect(toBookingLimitDatetime(null, departementCode)).toBeNull()
  })

  it('should convert yyyy-MM-dd string to UTC end-of-day ISO without milliseconds', () => {
    const result = toBookingLimitDatetime('2022-10-26', departementCode)

    expect(result).toBe('2022-10-26T21:59:59Z')
  })

  it('should convert Date instance to UTC end-of-day ISO without milliseconds', () => {
    const date = new Date('2022-10-26T00:00:00')

    const result = toBookingLimitDatetime(date, departementCode)

    expect(result).toBe('2022-10-26T21:59:59Z')
  })
})
