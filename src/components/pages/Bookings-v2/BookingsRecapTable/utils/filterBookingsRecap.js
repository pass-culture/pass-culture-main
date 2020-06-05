export const ALL_VENUES = 'all'

const filterByOfferName = (offerName, booking) => {
  if (offerName !== null) {
    const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
    return offerNameFromBooking.includes(offerName.toLowerCase())
  }
  return true
}

const extractDateFromDatetime = datetimeToExtract => {
  return datetimeToExtract.substr(0, 10)
}

const filterByOfferDate = (offerDate, booking) => {
  if (offerDate !== null) {
    const eventOfferDate = booking.stock.event_beginning_datetime
    if (eventOfferDate) {
      const offerDateFromBookingRecap = extractDateFromDatetime(eventOfferDate)
      return offerDateFromBookingRecap === offerDate
    }
    return false
  }
  return true
}

const filterBybookingBeginningDate = (bookingBeginningDate, booking) => {
  if (bookingBeginningDate !== null) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap >= bookingBeginningDate
  }
  return true
}

const filterByBookingEndDate = (bookingEndingDate, booking) => {
  if (bookingEndingDate !== null) {
    const offerDateFromBookingRecap = extractDateFromDatetime(booking.booking_date)
    return offerDateFromBookingRecap <= bookingEndingDate
  }
  return true
}

const filterByOfferVenue = (offerVenue, booking) => {
  if (offerVenue !== ALL_VENUES) {
    return booking.venue_identifier === offerVenue
  }
  return true
}

const filterBookingsRecap = (bookingsRecap, filters) => {
  const { offerName, offerDate, offerVenue, bookingBeginningDate, bookingEndingDate } = filters

  return bookingsRecap.filter(booking => {
    return (
      filterByOfferName(offerName, booking) &&
      filterByOfferDate(offerDate, booking) &&
      filterBybookingBeginningDate(bookingBeginningDate, booking) &&
      filterByBookingEndDate(bookingEndingDate, booking) &&
      filterByOfferVenue(offerVenue, booking)
    )
  })
}

export default filterBookingsRecap
