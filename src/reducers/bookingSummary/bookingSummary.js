const initialState = {
  bookingsFrom: '',
  bookingsTo: '',
  isFilteredByDigitalVenues: false,
  offerId: '',
  venueId: '',
}

export default (state = initialState, action = {}) => {
  switch (true) {
    case action.type === 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES':
      return Object.assign({}, state, {
        isFilteredByDigitalVenues: action.payload,
        bookingsFrom: '',
        bookingsTo: '',
        offerId: '',
        venueId: '',
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_VENUE_ID' && action.payload === 'all':
      return Object.assign({}, state, {
        bookingsFrom: '',
        bookingsTo: '',
        offerId: '',
        venueId: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_VENUE_ID' && action.payload !== 'all':
      return Object.assign({}, state, {
        bookingsFrom: '',
        bookingsTo: '',
        offerId: '',
        venueId: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_OFFER_ID' && action.payload === 'all':
      return Object.assign({}, state, {
        bookingsFrom: '',
        bookingsTo: '',
        offerId: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_OFFER_ID' && action.payload !== 'all':
      return Object.assign({}, state, {
        offerId: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM':
      return Object.assign({}, state, {
        bookingsFrom: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_UPDATE_BOOKINGS_TO':
      return Object.assign({}, state, {
        bookingsTo: action.payload,
      })
    default:
      return state
  }
}
