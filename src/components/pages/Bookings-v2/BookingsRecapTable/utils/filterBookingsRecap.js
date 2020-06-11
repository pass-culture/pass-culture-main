import { EMPTY_FILTER_VALUE } from '../Filters/Filters'

export const ALL_VENUES = 'all'

const matchOfferNameFilter = (offerName, booking) => {
  if (offerName !== EMPTY_FILTER_VALUE) {
    const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
    return offerNameFromBooking.includes(offerName.toLowerCase())
  }
  return true
}

const matchBookingBeneficiaryFilter = (bookingBeneficiary, booking) => {
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

const matchBookingTokenFilter = (bookingToken, booking) => {
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

const matchOfferDateFilter = (offerDate, booking) => {
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

const matchBookingBeginningDateFilter = (bookingBeginningDate, booking) => {
  if (bookingBeginningDate !== EMPTY_FILTER_VALUE) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap >= bookingBeginningDate
  }
  return true
}

const matchBookingEndDateFilter = (bookingEndingDate, booking) => {
  if (bookingEndingDate !== EMPTY_FILTER_VALUE) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap <= bookingEndingDate
  }
  return true
}

const matchOfferVenueFilter = (offerVenue, booking) => {
  if (offerVenue !== ALL_VENUES) {
    return booking.venue_identifier === offerVenue
  }
  return true
}

const matchISBNFilter = (isbn, booking) => {
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
      matchOfferNameFilter(offerName, booking) &&
      matchOfferDateFilter(offerDate, booking) &&
      matchBookingBeginningDateFilter(bookingBeginningDate, booking) &&
      matchBookingEndDateFilter(bookingEndingDate, booking) &&
      matchBookingBeneficiaryFilter(bookingBeneficiary, booking) &&
      matchBookingTokenFilter(bookingToken, booking) &&
      matchOfferVenueFilter(offerVenue, booking) &&
      matchISBNFilter(offerISBN, booking)
    )
  })
}

export default filterBookingsRecap
