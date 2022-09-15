import { BookingsFilters } from 'screens/Bookings/BookingsRecapTable/types'

export type BookingOmniSearchFilters = Pick<
  BookingsFilters,
  | 'bookingBeneficiary'
  | 'bookingToken'
  | 'offerISBN'
  | 'offerName'
  | 'bookingInstitution'
>
