import type { BookingsFilters } from '@/components/Bookings/BookingsFilters/types'

export type BookingOmniSearchFilters = Pick<
  BookingsFilters,
  | 'bookingBeneficiary'
  | 'bookingToken'
  | 'offerISBN'
  | 'offerName'
  | 'bookingInstitution'
  | 'bookingId'
>
