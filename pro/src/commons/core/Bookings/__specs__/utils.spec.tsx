import { BookingStatusFilter } from '@/apiClient/v1'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from '@/commons/utils/date'

import { DEFAULT_PRE_FILTERS } from '../constants'
import { buildBookingsRecapQuery } from '../utils'

describe('buildBookingsRecapQuery', () => {
  it('should use default filters when only offererId is passed in argument', () => {
    expect(buildBookingsRecapQuery({ offererId: '42', page: 1 })).toStrictEqual(
      {
        page: 1,
        offererId: '42',
        bookingPeriodBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
        bookingPeriodEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
        bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
      }
    )
  })

  it('should compute params with given prefilters', () => {
    const preFilters = {
      offererId: '42',
      offerVenueId: 'AY',
      offerEventDate: '2022-01-01',
      bookingBeginningDate: '2022-01-01',
      bookingEndingDate: '2022-01-02',
      bookingStatusFilter: BookingStatusFilter.REIMBURSED,
      page: 2,
    }

    expect(buildBookingsRecapQuery(preFilters)).toStrictEqual({
      offererId: '42',
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
