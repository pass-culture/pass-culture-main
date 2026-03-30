import type { BookingSortableColumn, SortOrder } from '@/apiClient/v1'

export type BookingsFilters = {
  bookingBeneficiary: string
  bookingToken: string
  offerISBN: string
  offerName: string
  bookingStatus: string[]
  selectedOmniSearchCriteria: string
  keywords: string
  bookingInstitution: string
  bookingId: string
  sortBy?: BookingSortableColumn
  sortOrder?: SortOrder
}
