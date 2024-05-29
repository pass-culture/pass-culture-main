import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import { EMPTY_FILTER_VALUE } from '../Filters/constants'
import { BookingsFilters } from '../types'

const doesOfferNameMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
  offerName: string,
  booking: T
): boolean => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = _sanitize(booking.stock.offerName)
    return offerNameFromBooking.includes(_sanitize(offerName))
  }
  return true
}

const doesBookingIdMatchFilter = <T extends CollectiveBookingResponseModel>(
  bookingId: string,
  booking: T
): boolean => {
  if (bookingId !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = _sanitize(booking.bookingId)
    return offerNameFromBooking.includes(_sanitize(bookingId))
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

const doesBookingInstitutionMatchFilter = (
  bookingInstitution: string,
  booking: CollectiveBookingResponseModel
): boolean => {
  if (bookingInstitution === EMPTY_FILTER_VALUE) {
    return true
  }

  const institutionSanitarized = _sanitize(bookingInstitution)
  const institutionFromBooking = _sanitize(
    `${booking.institution.institutionType} ${booking.institution.name}`.trim()
  )

  return institutionFromBooking.includes(institutionSanitarized)
}

const doesBookingTokenMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
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

const doesEANMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
  ean: string,
  booking: T
): boolean => {
  if (ean !== EMPTY_FILTER_VALUE) {
    return Boolean(
      booking.stock.offerIsbn && booking.stock.offerIsbn.includes(ean.trim())
    )
  }
  return true
}

const doesBookingStatusMatchFilter = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
  statuses: string[] | '',
  booking: T
): boolean => {
  if (statuses) {
    return !statuses.includes(booking.bookingStatus)
  }
  return true
}

const isBookingCollectiveBooking = (
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
): booking is CollectiveBookingResponseModel => booking.stock.offerIsEducational

export const filterBookingsRecap = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
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
    bookingInstitution,
    bookingId,
  } = filters

  return bookingsRecap.filter((booking) => {
    const matchFilters =
      doesOfferNameMatchFilter(offerName, booking) &&
      doesBookingStatusMatchFilter(bookingStatus, booking)

    if (isBookingCollectiveBooking(booking)) {
      return (
        matchFilters &&
        doesBookingInstitutionMatchFilter(bookingInstitution, booking) &&
        doesBookingIdMatchFilter(bookingId, booking)
      )
    }

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
