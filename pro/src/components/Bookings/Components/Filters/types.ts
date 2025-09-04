import type { BookingsFilters } from '../types'

export type BookingOmniSearchFilters = Pick<
  BookingsFilters,
  | 'bookingBeneficiary'
  | 'bookingToken'
  | 'offerISBN'
  | 'offerName'
  | 'bookingInstitution'
  | 'bookingId'
>
