import { api } from 'apiClient/api'
import { CollectiveBookingStatusFilter } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'commons/core/Bookings/constants'
import { PreFiltersParams } from 'commons/core/Bookings/types'
import { isDateValid } from 'commons/utils/date'
import { downloadFile } from 'commons/utils/downloadFile'

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
    // TODO fix PreFiltersParams type to use CollectiveBookingStatusFilter type
    // wait for squad eac to move collective on another page
    // @ts-expect-error
    filters.bookingStatusFilter as CollectiveBookingStatusFilter,
    isDateValid(filters.bookingBeginningDate)
      ? filters.bookingBeginningDate
      : null,
    isDateValid(filters.bookingEndingDate) ? filters.bookingEndingDate : null
  )

  const date = new Date().toISOString()
  downloadFile(bookingsCsvText, `reservations_eac_pass_culture-${date}.csv`)
}
