import { ALL_VENUES, EMPTY_FILTER_VALUE } from '../Filters/_constants'

const doesOfferNameMatchFilter = (offerName, booking) => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
    return offerNameFromBooking.includes(offerName.toLowerCase())
  }
  return true
}

const doesBookingBeneficiaryMatchFilter = (bookingBeneficiary, booking) => {
  if (bookingBeneficiary !== EMPTY_FILTER_VALUE) {
    const beneficiarySanitarized = bookingBeneficiary.toLowerCase().trim()
    const beneficiaryLastNameFromBooking = booking.beneficiary.lastname.toLowerCase()
    const beneficiaryFirstNameFromBooking = booking.beneficiary.firstname.toLowerCase()
    const beneficiaryEmailFromBooking = booking.beneficiary.email.toLowerCase()
    const FirstNameLastName = beneficiaryFirstNameFromBooking.concat(
      ' ',
      beneficiaryLastNameFromBooking
    )
    const LastNameFirstName = beneficiaryLastNameFromBooking.concat(
      ' ',
      beneficiaryFirstNameFromBooking
    )

    const isAPartOfName =
      beneficiaryLastNameFromBooking.includes(beneficiarySanitarized) ||
      beneficiaryFirstNameFromBooking.includes(beneficiarySanitarized) ||
      beneficiaryEmailFromBooking.includes(beneficiarySanitarized)
    const isFirstNameLastName = FirstNameLastName.includes(beneficiarySanitarized)
    const isLastNameFirstName = LastNameFirstName.includes(beneficiarySanitarized)

    return isAPartOfName || isFirstNameLastName || isLastNameFirstName
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
    return bookingTokenFromBooking.includes(bookingToken.toLowerCase())
  }
}

const extractDateFromDatetime = datetimeToExtract => {
  return datetimeToExtract.substr(0, 10)
}

const doesOfferDateMatchFilter = (offerDate, booking) => {
  if (offerDate !== EMPTY_FILTER_VALUE) {
    const eventOfferDate = booking.stock.event_beginning_datetime
    if (eventOfferDate) {
      const offerDateFromBookingRecap = extractDateFromDatetime(eventOfferDate)
      return offerDateFromBookingRecap === offerDate
    }
    return false
  }
  return true
}

const doesBookingBeginningDateMatchFilter = (bookingBeginningDate, booking) => {
  if (bookingBeginningDate !== EMPTY_FILTER_VALUE) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap >= bookingBeginningDate
  }
  return true
}

const doesBookingEndDateMatchFilter = (bookingEndingDate, booking) => {
  if (bookingEndingDate !== EMPTY_FILTER_VALUE) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap <= bookingEndingDate
  }
  return true
}

const doesOfferVenueMatchFilter = (offerVenue, booking) => {
  if (offerVenue && offerVenue !== ALL_VENUES) {
    return booking.venue.identifier === offerVenue
  }
  return true
}

const doesISBNMatchFilter = (isbn, booking) => {
  if (isbn !== EMPTY_FILTER_VALUE) {
    return booking.stock.type === 'book' && booking.stock.offer_isbn.includes(isbn)
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
    bookingBeginningDate,
    bookingEndingDate,
    offerDate,
    offerISBN,
    offerName,
    offerVenue,
    bookingStatus,
  } = filters
  return bookingsRecap.filter(booking => {
    return (
      doesOfferNameMatchFilter(offerName, booking) &&
      doesOfferDateMatchFilter(offerDate, booking) &&
      doesBookingBeginningDateMatchFilter(bookingBeginningDate, booking) &&
      doesBookingEndDateMatchFilter(bookingEndingDate, booking) &&
      doesBookingBeneficiaryMatchFilter(bookingBeneficiary, booking) &&
      doesBookingStatusMatchFilter(bookingStatus, booking) &&
      doesBookingTokenMatchFilter(bookingToken, booking) &&
      doesOfferVenueMatchFilter(offerVenue, booking) &&
      doesISBNMatchFilter(offerISBN, booking)
    )
  })
}

export default filterBookingsRecap
