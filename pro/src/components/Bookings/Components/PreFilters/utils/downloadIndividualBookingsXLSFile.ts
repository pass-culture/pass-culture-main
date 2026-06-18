import { api } from '@/apiClient/api'
import type { getBookingsExcelData } from '@/apiClient/v1'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { isDateValid } from '@/commons/utils/date'
import { downloadFile } from '@/commons/utils/downloadFile'

export const downloadIndividualBookingsXLSFile = async (
  filters: PreFiltersParams & { page?: number },
  offererId: number
) => {
  const query: getBookingsExcelData['query'] = {
    offererId,
    page: filters.page,
    offerId: null,
    eventDate:
      filters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate &&
      isDateValid(filters.offerEventDate)
        ? filters.offerEventDate
        : null,
    bookingStatusFilter: filters.bookingStatusFilter,
    bookingPeriodBeginningDate: isDateValid(filters.bookingBeginningDate)
      ? filters.bookingBeginningDate
      : null,
    bookingPeriodEndingDate: isDateValid(filters.bookingEndingDate)
      ? filters.bookingEndingDate
      : null,
    offererAddressId:
      filters.offererAddressId !== DEFAULT_PRE_FILTERS.offererAddressId
        ? Number(filters.offererAddressId)
        : null,
  }

  const bookingsXLSText = (await api.getBookingsExcel({ query })) as Blob

  const date = new Date().toISOString()
  downloadFile(bookingsXLSText, `reservations_pass_culture-${date}.xlsx`)
}
