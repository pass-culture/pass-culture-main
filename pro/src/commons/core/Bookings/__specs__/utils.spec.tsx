import { BookingStatusFilter } from 'apiClient/v1'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'commons/utils/date'

import { DEFAULT_PRE_FILTERS } from '../constants'
import {
  bookingStatusFilterOrNull,
  buildBookingsRecapQuery,
  isBookingStatusFilter,
} from '../utils'

describe('buildBookingsRecapQuery', () => {
  it('should use default filters when no filters is passed in argument', () => {
    expect(buildBookingsRecapQuery({ page: 1 })).toStrictEqual({
      page: 1,
      bookingPeriodBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
      bookingPeriodEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
      bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
    })
  })

  it('should compute params with given prefilters', () => {
    const preFilters = {
      offerVenueId: 'AY',
      offerEventDate: '2022-01-01',
      bookingBeginningDate: '2022-01-01',
      bookingEndingDate: '2022-01-02',
      bookingStatusFilter: BookingStatusFilter.REIMBURSED,
      page: 2,
    }

    expect(buildBookingsRecapQuery(preFilters)).toStrictEqual({
      venueId: 'AY',
      eventDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-01T10:00:00.000Z'),
        FORMAT_ISO_DATE_ONLY
      ),
      bookingPeriodBeginningDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-01T00:00:00.000Z'),
        FORMAT_ISO_DATE_ONLY
      ),
      bookingPeriodEndingDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-02T00:00:00.000Z'),
        FORMAT_ISO_DATE_ONLY
      ),
      bookingStatusFilter: BookingStatusFilter.REIMBURSED,
      page: 2,
    })
  })
})

describe('isBookingStatusFilter', () => {
  it('should return true for a valid BookingStatusFilter value', () => {
    expect(isBookingStatusFilter(BookingStatusFilter.BOOKED)).toBe(true)
    expect(isBookingStatusFilter(BookingStatusFilter.VALIDATED)).toBe(true)
    expect(isBookingStatusFilter(BookingStatusFilter.REIMBURSED)).toBe(true)
  })

  it('should return false for invalid values', () => {
    expect(isBookingStatusFilter('invalid')).toBe(false)
    expect(isBookingStatusFilter(null)).toBe(false)
    expect(isBookingStatusFilter(undefined)).toBe(false)
    expect(isBookingStatusFilter(123)).toBe(false)
    expect(isBookingStatusFilter({})).toBe(false)
    expect(isBookingStatusFilter([])).toBe(false)
  })
})

describe('bookingStatusFilterOrNull', () => {
  it('should return the value if it is a valid BookingStatusFilter', () => {
    expect(bookingStatusFilterOrNull(BookingStatusFilter.BOOKED)).toBe(
      BookingStatusFilter.BOOKED
    )
    expect(bookingStatusFilterOrNull(BookingStatusFilter.VALIDATED)).toBe(
      BookingStatusFilter.VALIDATED
    )
    expect(bookingStatusFilterOrNull(BookingStatusFilter.REIMBURSED)).toBe(
      BookingStatusFilter.REIMBURSED
    )
  })

  it('should return null for invalid values', () => {
    expect(bookingStatusFilterOrNull('invalid')).toBe(null)
    expect(bookingStatusFilterOrNull(null)).toBe(null)
    expect(bookingStatusFilterOrNull(undefined)).toBe(null)
    expect(bookingStatusFilterOrNull(123)).toBe(null)
    expect(bookingStatusFilterOrNull({})).toBe(null)
    expect(bookingStatusFilterOrNull([])).toBe(null)
  })
})
