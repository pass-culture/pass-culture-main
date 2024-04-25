import { api } from 'apiClient/api'
import { CollectiveBookingStatusFilter } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { downloadFile } from 'utils/downloadFile'

export const downloadCollectiveBookingsCSVFile = async (
  filters: PreFiltersParams & { page?: number }
) => {
  const bookingsCsvText = await api.getCollectiveBookingsCsv(
    filters.page,
    filters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
      ? Number(filters.offerVenueId)
      : null,
    filters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate
      ? filters.offerEventDate
      : null,
    // TODO fix PreFiltersParams type to use CollectiveBookingStatusFilter type
    // @ts-expect-error
    filters.bookingStatusFilter as CollectiveBookingStatusFilter,
    filters.bookingBeginningDate,
    filters.bookingEndingDate
  )

  const date = new Date().toISOString()
  downloadFile(
    bookingsCsvText,
    `reservations_eac_pass_culture-${date}.csv`,
    'text/csv'
  )
}
