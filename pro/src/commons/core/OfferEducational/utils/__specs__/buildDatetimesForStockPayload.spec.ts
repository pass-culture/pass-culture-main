import {
  buildBookingLimitDatetimeForStockPayload,
  buildDatetimeForStockPayload,
} from '../buildDatetimesForStockPayload'

describe('buildDatetimeForStockPayload', () => {
  it('should return datetime in UTC without millisecond', () => {
    const datetime = '2024-06-21'
    const eventTime = '03:45'
    const departmentCode = '972'

    expect(
      buildDatetimeForStockPayload(datetime, eventTime, departmentCode)
    ).toBe('2024-06-21T07:45:00Z')
  })
})

describe('buildBookingLimitDatetimeForStockPayload', () => {
  it('should return start datetime in user timezone when booking limit datetime is not valid', () => {
    const bookingLimitDatetime = ''
    const startDatetime = '2024-06-21'
    const eventTime = '03:45'
    const departmentCode = '56'

    expect(
      buildBookingLimitDatetimeForStockPayload(
        startDatetime,
        eventTime,
        bookingLimitDatetime,
        departmentCode
      )
    ).toBe('2024-06-21T01:45:00Z')
  })

  it('should return start datetime in user timezone when booking limit datetime is the same as start datetime', () => {
    const bookingLimitDatetime = '2024-06-21'
    const startDatetime = '2024-06-21'
    const eventTime = '03:45'
    const departmentCode = '56'

    expect(
      buildBookingLimitDatetimeForStockPayload(
        startDatetime,
        eventTime,
        bookingLimitDatetime,
        departmentCode
      )
    ).toBe('2024-06-21T01:45:00Z')
  })

  it('should return the end of the booking limit datetime when it is different from the start datetime', () => {
    const bookingLimitDatetime = '2024-06-15'
    const startDatetime = '2024-06-21'
    const eventTime = '03:45'
    const departmentCode = '56'

    expect(
      buildBookingLimitDatetimeForStockPayload(
        startDatetime,
        eventTime,
        bookingLimitDatetime,
        departmentCode
      )
    ).toBe('2024-06-15T21:59:59Z')
  })
})
