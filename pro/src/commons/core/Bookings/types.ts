import type { BookingStatusFilter } from '@/apiClient/v1/new'

export type PreFiltersParams = {
  offererAddressId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  bookingStatusFilter: BookingStatusFilter
}
