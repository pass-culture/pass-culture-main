import { apiNew } from '@/apiClient/api'
import type { getBookingsCsvData } from '@/apiClient/v1/new'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { isDateValid } from '@/commons/utils/date'
import { downloadFile } from '@/commons/utils/downloadFile'

export const downloadIndividualBookingsCSVFile = async (
  filters: PreFiltersParams & { page?: number },
  offererId: number
) => {
  const query: getBookingsCsvData['query'] = {
    offererId,
    page: filters.page ?? 1,
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

  const bookingsCsvText = (await apiNew.getBookingsCsv({ query })) as string
  const bookingsCsvBlob = new Blob([bookingsCsvText], {
    type: 'text/csv;charset=utf-8;',
  })

  const date = new Date().toISOString()
  downloadFile(bookingsCsvBlob, `reservations_pass_culture-${date}.csv`)
}
