import { api } from 'apiClient/api'
import {
  BookingStatusFilter,
  CollectiveBookingStatusFilter,
} from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { isDateValid } from 'utils/date'
import { downloadFile } from 'utils/downloadFile'

const bookingStatusFilterToCollectiveBookingStatusFilter = (
  bookingStatusFilter: BookingStatusFilter
) => {
  switch (bookingStatusFilter) {
    case BookingStatusFilter.BOOKED:
      return CollectiveBookingStatusFilter.BOOKED
    case BookingStatusFilter.REIMBURSED:
      return CollectiveBookingStatusFilter.REIMBURSED
    case BookingStatusFilter.VALIDATED:
      return CollectiveBookingStatusFilter.VALIDATED
  }
}

export const downloadCollectiveBookingsCSVFile = async (
  filters: PreFiltersParams & { page?: number }
) => {
  const bookingsCsvText = await api.getCollectiveBookingsCsv(
    filters.page,
    filters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
      ? Number(filters.offerVenueId)
      : null,
    filters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate &&
      isDateValid(filters.offerEventDate)
      ? filters.offerEventDate
      : null,
    bookingStatusFilterToCollectiveBookingStatusFilter(
      filters.bookingStatusFilter
    ),
    isDateValid(filters.bookingBeginningDate)
      ? filters.bookingBeginningDate
      : null,
    isDateValid(filters.bookingEndingDate) ? filters.bookingEndingDate : null
  )

  const date = new Date().toISOString()
  downloadFile(bookingsCsvText, `reservations_eac_pass_culture-${date}.csv`)
}
