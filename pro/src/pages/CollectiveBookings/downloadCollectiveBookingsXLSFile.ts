import { api } from 'apiClient/api'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { downloadFile } from 'utils/downloadFile'

export const downloadCollectiveBookingsXLSFile = async (
  filters: PreFiltersParams & { page?: number }
) => {
  const bookingsXLSText = await api.getCollectiveBookingsExcel(
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
    new Uint8Array(bookingsXLSText),
    `reservations_eac_pass_culture-${date}.xlsx`,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  )
}
