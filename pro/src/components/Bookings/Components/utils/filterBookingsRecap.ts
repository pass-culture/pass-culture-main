import type { BookingRecapResponseModel } from '@/apiClient/v1'

import { EMPTY_FILTER_VALUE } from '../Filters/constants'
import type { BookingsFilters } from '../types'

const doesOfferNameMatchFilter = <T extends BookingRecapResponseModel>(
  offerName: string,
  booking: T
): boolean => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = _sanitize(booking.stock.offerName)
    return offerNameFromBooking.includes(_sanitize(offerName))
  }
  return true
}

const doesBookingBeneficiaryMatchFilter = (
  bookingBeneficiary: string,
  booking: BookingRecapResponseModel
): boolean => {
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
      referential.filter((item) => item.includes(beneficiarySanitarized))
        .length > 0
    )
  }
  return true
}

const doesBookingTokenMatchFilter = <T extends BookingRecapResponseModel>(
  bookingToken: string,
  booking: T
): boolean => {
  if (bookingToken === EMPTY_FILTER_VALUE) {
    return true
  } else if (booking.bookingToken === null) {
    return false
  } else {
    const bookingTokenFromBooking = booking.bookingToken?.toLowerCase()
    return Boolean(
      bookingTokenFromBooking?.includes(bookingToken.toLowerCase().trim())
    )
  }
}

const doesEANMatchFilter = <T extends BookingRecapResponseModel>(
  ean: string,
  booking: T
): boolean => {
  if (ean !== EMPTY_FILTER_VALUE) {
    return Boolean(booking.stock.offerEan?.includes(ean.trim()))
  }
  return true
}

const doesBookingStatusMatchFilter = <T extends BookingRecapResponseModel>(
  statuses: string[] | '',
  booking: T
): boolean => {
  if (statuses) {
    return !statuses.includes(booking.bookingStatus)
  }
  return true
}

export const filterBookingsRecap = <T extends BookingRecapResponseModel>(
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

  return bookingsRecap.filter((booking) => {
    const matchFilters =
      doesOfferNameMatchFilter(offerName, booking) &&
      doesBookingStatusMatchFilter(bookingStatus, booking)

    return (
      matchFilters &&
      doesBookingBeneficiaryMatchFilter(bookingBeneficiary, booking) &&
      doesBookingTokenMatchFilter(bookingToken, booking) &&
      doesEANMatchFilter(offerISBN, booking)
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
