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
    const res = buildDatetimesForStock(BASE_DATES, '75')

    expect(res.startDatetime).toBe('2024-06-15T12:30:00Z')
    expect(res.endDatetime).toBe('2024-06-20T12:30:00Z')
    expect(res.bookingLimitDatetime).toBe('2024-06-10T21:59:59Z')
  })

  it('should return different datetimes if departementCode is in different timezone', () => {
    const res31 = buildDatetimesForStock(BASE_DATES, '31')
    const res971 = buildDatetimesForStock(BASE_DATES, '971')

    expect(res31.startDatetime).not.toBe(res971.startDatetime)
    expect(res31.endDatetime).not.toBe(res971.endDatetime)
    expect(res31.bookingLimitDatetime).not.toBe(res971.bookingLimitDatetime)
  })

  it('should set booking limit datetime at start datetime in user timezone when booking limit date empty', () => {
    const res = buildDatetimesForStock(
      { ...BASE_DATES, bookingLimitDate: '' },
      '31'
    )
    expect(res.bookingLimitDatetime).toBe('2024-06-15T12:30:00Z')
  })

  it('should set booking limit datetime at start datetime in user timezone when both given dates are the same', () => {
    const res = buildDatetimesForStock(
      { ...BASE_DATES, bookingLimitDate: BASE_DATES.startDate },
      '31'
    )
    expect(res.bookingLimitDatetime).toBe('2024-06-15T12:30:00Z')
  })

  it('should set booking limit datetime at the end of the given day', () => {
    const res = buildDatetimesForStock(
      { ...BASE_DATES, bookingLimitDate: '2024-06-10' },
      '31'
    )
    expect(res.bookingLimitDatetime).toBe('2024-06-10T21:59:59Z')
  })
})
