import type { CollectiveStockFormDates } from '../../types'
import { buildDatetimesForStock } from '../buildDatetimesForStock'

const BASE_DATES: CollectiveStockFormDates = {
  startDate: '2024-06-15',
  endDate: '2024-06-20',
  eventTime: '14:30',
  bookingLimitDate: '2024-06-10',
}

describe('buildDatetimesForStock', () => {
  it('should return correctly formatted datetimes', () => {
    const result = buildDatetimesForStock(BASE_DATES, '75')

    expect(result.startDatetime).toBe('2024-06-15T12:30:00Z')
    expect(result.endDatetime).toBe('2024-06-20T12:30:00Z')
    expect(result.bookingLimitDatetime).toBe('2024-06-10T21:59:59Z')
  })

  it('should return different datetimes if departementCode is in different timezone', () => {
    const result75 = buildDatetimesForStock(BASE_DATES, '75')
    const result971 = buildDatetimesForStock(BASE_DATES, '971')

    expect(result75.startDatetime).not.toBe(result971.startDatetime)
    expect(result75.endDatetime).not.toBe(result971.endDatetime)
    expect(result75.bookingLimitDatetime).not.toBe(
      result971.bookingLimitDatetime
    )
  })
})

// describe('buildBookingLimitDatetimeForStockPayload', () => {
//   it('should return start datetime in user timezone when booking limit datetime is not valid', () => {
//     const bookingLimitDatetime = ''
//     const startDatetime = '2024-06-21'
//     const eventTime = '03:45'
//     const departmentCode = '56'

//     expect(
//       buildBookingLimitDatetimeForStockPayload(
//         startDatetime,
//         eventTime,
//         bookingLimitDatetime,
//         departmentCode
//       )
//     ).toBe('2024-06-21T01:45:00Z')
//   })

//   it('should return start datetime in user timezone when booking limit datetime is the same as start datetime', () => {
//     const bookingLimitDatetime = '2024-06-21'
//     const startDatetime = '2024-06-21'
//     const eventTime = '03:45'
//     const departmentCode = '56'

//     expect(
//       buildBookingLimitDatetimeForStockPayload(
//         startDatetime,
//         eventTime,
//         bookingLimitDatetime,
//         departmentCode
//       )
//     ).toBe('2024-06-21T01:45:00Z')
//   })

//   it('should return the end of the booking limit datetime when it is different from the start datetime', () => {
//     const bookingLimitDatetime = '2024-06-15'
//     const startDatetime = '2024-06-21'
//     const eventTime = '03:45'
//     const departmentCode = '56'

//     expect(
//       buildBookingLimitDatetimeForStockPayload(
//         startDatetime,
//         eventTime,
//         bookingLimitDatetime,
//         departmentCode
//       )
//     ).toBe('2024-06-15T21:59:59Z')
//   })
// })
