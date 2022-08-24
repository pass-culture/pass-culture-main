import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import { EMPTY_FILTER_VALUE } from '../components/Filters/_constants'
import { BookingsFilters } from '../types'

const doesOfferNameMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  offerName: string,
  booking: T
) => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = _sanitize(booking.stock.offer_name)
    return offerNameFromBooking.includes(_sanitize(offerName))
  }
  return true
}

const doesBookingBeneficiaryMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  bookingBeneficiary: string,
  booking: T
) => {
  if (bookingBeneficiary !== EMPTY_FILTER_VALUE) {
    const beneficiarySanitarized = _sanitize(bookingBeneficiary)
    const beneficiaryLastNameFromBooking = booking.beneficiary.lastname
      ? _sanitize(booking.beneficiary.lastname)
      : ''
    const beneficiaryFirstNameFromBooking = booking.beneficiary.firstname
      ? _sanitize(booking.beneficiary.firstname)
      : ''
    const beneficiaryEmailFromBooking = booking.beneficiary.email
      ? _sanitize(booking.beneficiary.email)
      : ''

    const firstNameLastName = beneficiaryFirstNameFromBooking.concat(
      ' ',
      beneficiaryLastNameFromBooking
    )
    const lastNameFirstName = beneficiaryLastNameFromBooking.concat(
      ' ',
      beneficiaryFirstNameFromBooking
    )

    const referential = [
      beneficiaryLastNameFromBooking,
      beneficiaryFirstNameFromBooking,
      beneficiaryEmailFromBooking,
      firstNameLastName,
      lastNameFirstName,
    ]
    return (
      referential.filter(item => item.includes(beneficiarySanitarized)).length >
      0
    )
  }
  return true
}

const doesBookingTokenMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  bookingToken: string,
  booking: T
) => {
  if (bookingToken === EMPTY_FILTER_VALUE) {
    return true
  } else if (booking.booking_token === null) {
    return false
  } else {
    const bookingTokenFromBooking = booking.booking_token?.toLowerCase()
    return bookingTokenFromBooking?.includes(bookingToken.toLowerCase().trim())
  }
}

const doesISBNMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  isbn: string,
  booking: T
) => {
  if (isbn !== EMPTY_FILTER_VALUE) {
    return (
      booking.stock.offer_isbn && booking.stock.offer_isbn.includes(isbn.trim())
    )
  }
  return true
}

const doesBookingStatusMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  statuses: string[] | '',
  booking: T
) => {
  if (statuses) {
    return !statuses.includes(booking.booking_status)
  }
  return true
}

const filterBookingsRecap = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  bookingsRecap: T[],
  filters: BookingsFilters
): T[] => {
  const {
    bookingBeneficiary,
    bookingToken,
    offerISBN,
    offerName,
    bookingStatus,
  } = filters

  return bookingsRecap.filter(booking => {
    return (
      doesOfferNameMatchFilter(offerName, booking) &&
      doesBookingBeneficiaryMatchFilter(bookingBeneficiary, booking) &&
      doesBookingStatusMatchFilter(bookingStatus, booking) &&
      doesBookingTokenMatchFilter(bookingToken, booking) &&
      doesISBNMatchFilter(offerISBN, booking)
    )
  })
}

const _sanitize = (input: string): string => {
  const REMOVE_ACCENTS_REGEX = /[\u0300-\u036f]/g
  return input
    .normalize('NFD')
    .replace(REMOVE_ACCENTS_REGEX, '')
    .trim()
    .toLowerCase()
}

export default filterBookingsRecap
