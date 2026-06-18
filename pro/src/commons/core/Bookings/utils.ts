import type { GetBookingsProQueryModel } from '@/apiClient/v1'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'

export const buildBookingsRecapQuery = ({
  offererAddressId = DEFAULT_PRE_FILTERS.offererAddressId,
  offerEventDate = DEFAULT_PRE_FILTERS.offerEventDate,
  bookingBeginningDate = DEFAULT_PRE_FILTERS.bookingBeginningDate,
  bookingEndingDate = DEFAULT_PRE_FILTERS.bookingEndingDate,
  bookingStatusFilter = DEFAULT_PRE_FILTERS.bookingStatusFilter,
  page,
}: Partial<PreFiltersParams> & {
  page?: number
}): Partial<GetBookingsProQueryModel> => {
  const params: Partial<GetBookingsProQueryModel> = { page }

  if (offererAddressId !== DEFAULT_PRE_FILTERS.offererAddressId) {
    params.offererAddressId = Number(offererAddressId)
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

  params.bookingStatusFilter = bookingStatusFilter

  return params
}
