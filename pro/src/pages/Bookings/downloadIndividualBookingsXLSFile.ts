import { api } from 'apiClient/api'
import { OfferType } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { downloadFile } from 'utils/downloadFile'

import { isDateValid } from './../../utils/date'

export const downloadIndividualBookingsXLSFile = async (
  filters: PreFiltersParams & { page?: number }
) => {
  const bookingsXLSText = await api.getBookingsExcel(
    filters.page,
    filters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
      ? Number(filters.offerVenueId)
      : null,
    null,
    filters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate &&
      isDateValid(filters.offerEventDate)
      ? filters.offerEventDate
      : null,
    filters.bookingStatusFilter,
    isDateValid(filters.bookingBeginningDate)
      ? filters.bookingBeginningDate
      : null,
    isDateValid(filters.bookingEndingDate) ? filters.bookingEndingDate : null,
    // TODO fix PreFiltersParams type to use OfferType instead of string
    filters.offerType !== DEFAULT_PRE_FILTERS.offerType
      ? (filters.offerType as OfferType)
      : null
  )
  const date = new Date().toISOString()
  downloadFile(bookingsXLSText, `reservations_pass_culture-${date}.xlsx`)
}
