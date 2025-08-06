import { BookingsFilters } from '@/components/Bookings/BookingsRecapTable/types'

export type BookingOmniSearchFilters = Pick<
  BookingsFilters,
  | 'bookingBeneficiary'
  | 'bookingToken'
  | 'offerISBN'
  | 'offerName'
  | 'bookingInstitution'
  | 'bookingId'
>
