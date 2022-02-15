export type BookingsRecap = {
  bookings_recap: Record<string, string>[]
  page: number
  pages: number
  total: number
}

enum BookingOfferType {
  BIEN = 'BIEN',
  EVENEMENT = 'EVENEMENT',
}

enum BookingFormula {
  PLACE = 'PLACE',
  ABO = 'ABO',
  VOID = '',
}

export type Booking = {
  bookingId: string
  dateOfBirth: string
  datetime: string
  ean13?: string
  email: string
  formula: BookingFormula
  isUsed: boolean
  offerId: number
  publicOfferId: string
  offerName: string
  offerType: BookingOfferType
  phoneNumber: string
  price: number
  quantity: number
  theater: Record<string, string>
  userName: string
  venueAddress?: string
  venueDepartmentCode?: string
  venueName: string
}
