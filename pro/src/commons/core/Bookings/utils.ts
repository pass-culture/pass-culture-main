import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { APIFilters, PreFiltersParams } from '@/commons/core/Bookings/types'

export const buildBookingsRecapQuery = ({
  offererId = DEFAULT_PRE_FILTERS.offererId,
  offerVenueId = DEFAULT_PRE_FILTERS.offerVenueId,
  offererAddressId = DEFAULT_PRE_FILTERS.offererAddressId,
  offerEventDate = DEFAULT_PRE_FILTERS.offerEventDate,
  bookingBeginningDate = DEFAULT_PRE_FILTERS.bookingBeginningDate,
  bookingEndingDate = DEFAULT_PRE_FILTERS.bookingEndingDate,
  bookingStatusFilter = DEFAULT_PRE_FILTERS.bookingStatusFilter,
  offerId,
  page,
}: Partial<PreFiltersParams> & { page?: number }): APIFilters => {
  const params = { page } as APIFilters

  if (offererId !== DEFAULT_PRE_FILTERS.offererId) {
    params.offererId = offererId
  }

  if (offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId) {
    params.venueId = offerVenueId
  }
  if (offererAddressId !== DEFAULT_PRE_FILTERS.offererAddressId) {
    params.offererAddressId = offererAddressId
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
