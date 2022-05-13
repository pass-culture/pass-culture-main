import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'

import { BookingStatusFilter } from 'api/v1/gen'
import { DEFAULT_PRE_FILTERS } from '../constants'
import { buildBookingsRecapQuery } from '../utils'

describe('buildBookingsRecapQuery', () => {
  it('should use default filters when no filters is passed in argument', () => {
    expect(buildBookingsRecapQuery({ page: 1 })).toStrictEqual({
      page: 1,
      bookingPeriodBeginningDate: formatBrowserTimezonedDateAsUTC(
        DEFAULT_PRE_FILTERS.bookingBeginningDate,
        FORMAT_ISO_DATE_ONLY
      ),
      bookingPeriodEndingDate: formatBrowserTimezonedDateAsUTC(
        DEFAULT_PRE_FILTERS.bookingEndingDate,
        FORMAT_ISO_DATE_ONLY
      ),
      bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
    })
  })

  it('should compute params with given prefilters', () => {
    const preFilters = {
      offerVenueId: 'AY',
      offerEventDate: new Date('2022-01-01T10:00:00.000Z'),
      bookingBeginningDate: new Date('2022-01-01T00:00:00.000Z'),
      bookingEndingDate: new Date('2022-01-02T00:00:00.000Z'),
      bookingStatusFilter: BookingStatusFilter.Reimbursed,
      offerType: 'individual',
      page: 2,
    }

    expect(buildBookingsRecapQuery(preFilters)).toStrictEqual({
      venueId: 'AY',
      offerType: 'individual',
      eventDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-01T10:00:00.000Z')
      ),
      bookingPeriodBeginningDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-01T00:00:00.000Z'),
        FORMAT_ISO_DATE_ONLY
      ),
      bookingPeriodEndingDate: formatBrowserTimezonedDateAsUTC(
        new Date('2022-01-02T00:00:00.000Z'),
        FORMAT_ISO_DATE_ONLY
      ),
      bookingStatusFilter: BookingStatusFilter.Reimbursed,
      page: 2,
    })
  })
})
