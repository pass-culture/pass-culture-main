import { EMPTY_FILTER_VALUE } from '../Filters/Filters'

export const ALL_VENUES = 'all'

const doesOfferNameMatchFilter = (offerName, booking) => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
    return offerNameFromBooking.includes(offerName.toLowerCase())
  }
  return true
}

const doesBookingBeneficiaryMatchFilter = (bookingBeneficiary, booking) => {
  if (bookingBeneficiary !== EMPTY_FILTER_VALUE) {
    const beneficiaryLowercase = bookingBeneficiary.toLowerCase()
    const beneficiaryLastNameFromBooking = booking.beneficiary.lastname.toLowerCase()
    const beneficiaryFirstNameFromBooking = booking.beneficiary.firstname.toLowerCase()
    const beneficiaryEmailFromBooking = booking.beneficiary.email.toLowerCase()

    return (
      beneficiaryLastNameFromBooking.includes(beneficiaryLowercase) ||
      beneficiaryFirstNameFromBooking.includes(beneficiaryLowercase) ||
      beneficiaryEmailFromBooking.includes(beneficiaryLowercase)
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
  if (offerVenue !== ALL_VENUES) {
    return booking.venue_identifier === offerVenue
  }
  return true
}

const doesISBNMatchFilter = (isbn, booking) => {
  if (isbn !== EMPTY_FILTER_VALUE) {
    return booking.stock.type === 'book' && booking.stock.offer_isbn.includes(isbn)
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
  } = filters
  return bookingsRecap.filter(booking => {
    return (
      doesOfferNameMatchFilter(offerName, booking) &&
      doesOfferDateMatchFilter(offerDate, booking) &&
      doesBookingBeginningDateMatchFilter(bookingBeginningDate, booking) &&
      doesBookingEndDateMatchFilter(bookingEndingDate, booking) &&
      doesBookingBeneficiaryMatchFilter(bookingBeneficiary, booking) &&
      doesBookingTokenMatchFilter(bookingToken, booking) &&
      doesOfferVenueMatchFilter(offerVenue, booking) &&
      doesISBNMatchFilter(offerISBN, booking)
    )
  })
}

export default filterBookingsRecap
