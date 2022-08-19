import { EMPTY_FILTER_VALUE } from '../Filters/_constants'

const doesOfferNameMatchFilter = (offerName, booking) => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = _sanitize(booking.stock.offer_name)
    return offerNameFromBooking.includes(_sanitize(offerName))
  }
  return true
}

const doesBookingBeneficiaryMatchFilter = (bookingBeneficiary, booking) => {
  if (bookingBeneficiary !== EMPTY_FILTER_VALUE) {
    const beneficiarySanitarized = _sanitize(bookingBeneficiary)
    const beneficiaryLastNameFromBooking = _sanitize(
      booking.beneficiary.lastname
    )
    const beneficiaryFirstNameFromBooking = _sanitize(
      booking.beneficiary.firstname
    )
    const beneficiaryEmailFromBooking = _sanitize(booking.beneficiary.email)

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

const doesBookingTokenMatchFilter = (bookingToken, booking) => {
  if (bookingToken === EMPTY_FILTER_VALUE) {
    return true
  } else if (booking.booking_token === null) {
    return false
  } else {
    const bookingTokenFromBooking = booking.booking_token.toLowerCase()
    return bookingTokenFromBooking.includes(bookingToken.toLowerCase().trim())
  }
}

const doesISBNMatchFilter = (isbn, booking) => {
  if (isbn !== EMPTY_FILTER_VALUE) {
    return (
      booking.stock.offer_isbn && booking.stock.offer_isbn.includes(isbn.trim())
    )
  }
  return true
}

const doesBookingStatusMatchFilter = (statuses, booking) => {
  if (statuses && statuses !== EMPTY_FILTER_VALUE) {
    return !statuses.includes(booking.booking_status)
  }
  return true
}

const filterBookingsRecap = (bookingsRecap, filters) => {
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

const _sanitize = input => {
  const REMOVE_ACCENTS_REGEX = /[\u0300-\u036f]/g
  return input
    .normalize('NFD')
    .replace(REMOVE_ACCENTS_REGEX, '')
    .trim()
    .toLowerCase()
}

export default filterBookingsRecap
