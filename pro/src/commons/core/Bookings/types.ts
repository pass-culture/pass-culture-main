import type { BookingStatusFilter } from '@/apiClient/v1'

export type PreFiltersParams = {
  offererAddressId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  bookingStatusFilter: BookingStatusFilter
}
