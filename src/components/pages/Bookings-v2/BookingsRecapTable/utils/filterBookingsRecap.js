const filterByOfferName = (offerName, booking) => {
  if (offerName !== null) {
    const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
    return offerNameFromBooking.includes(offerName.toLowerCase())
  }
  return true
}

const filterByOfferDate = (offerDate, booking) => {
  if (offerDate !== null) {
    const eventOfferDate = booking.stock.event_beginning_datetime
    if (eventOfferDate) {
      const offerDateFromBookingRecap = eventOfferDate.substr(0, 10)
      return offerDateFromBookingRecap === offerDate
    }
    return false
  }
  return true
}

const filterBookingsRecap = (bookingsRecap, filters) => {
  const { offerName, offerDate } = filters

  return bookingsRecap.filter(booking => {
    return filterByOfferName(offerName, booking) && filterByOfferDate(offerDate, booking)
  })
}

export default filterBookingsRecap
