import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { APIFilters, PreFiltersParams } from 'core/Bookings/types'

export const buildBookingsRecapQuery = ({
  offerVenueId = DEFAULT_PRE_FILTERS.offerVenueId,
  offerEventDate = DEFAULT_PRE_FILTERS.offerEventDate,
  bookingBeginningDate = DEFAULT_PRE_FILTERS.bookingBeginningDate,
  bookingEndingDate = DEFAULT_PRE_FILTERS.bookingEndingDate,
  bookingStatusFilter = DEFAULT_PRE_FILTERS.bookingStatusFilter,
  offerId,
  page,
}: Partial<PreFiltersParams> & { page?: number }): APIFilters => {
  const params = { page } as APIFilters

  if (offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId) {
    params.venueId = offerVenueId
  }
  if (offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate) {
    params.eventDate = offerEventDate
  }
  if (bookingBeginningDate) {
    params.bookingPeriodBeginningDate = bookingBeginningDate
  }

  if (bookingEndingDate) {
    params.bookingPeriodEndingDate = bookingEndingDate
  }

  if (offerId) {
    params.offerId = offerId
  }

  params.bookingStatusFilter = bookingStatusFilter

  return params
}
