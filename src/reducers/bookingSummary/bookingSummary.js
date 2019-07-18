const initialState = {
  isFilterByDigitalVenues: false,
  selectedVenue: '',
  selectedOffer: '',
  selectOffersFrom: '',
  selectOffersTo: '',
}

export default (state = initialState, action = {}) => {
  switch (true) {
    case action.type === 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE':
      return Object.assign({}, state, {
        isFilterByDigitalVenues: action.payload,
        selectedOffer: '',
        selectedVenue: '',
      })
    case action.type === 'BOOKING_SUMMARY_SELECT_VENUE' && action.payload === 'all':
      return Object.assign({}, state, {
        selectedOffer: '',
        selectedVenue: action.payload,
        selectOffersFrom: '',
        selectOffersTo: '',
      })
    case action.type === 'BOOKING_SUMMARY_SELECT_VENUE' && action.payload !== 'all':
      return Object.assign({}, state, {
        selectedOffer: '',
        selectedVenue: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_SELECT_OFFER' && action.payload === 'all':
      return Object.assign({}, state, {
        selectedOffer: action.payload,
        selectOffersFrom: '',
        selectOffersTo: '',
      })
    case action.type === 'BOOKING_SUMMARY_SELECT_OFFER' && action.payload !== 'all':
      return Object.assign({}, state, {
        selectedOffer: action.payload,
      })
    case action.type === 'BOOKING_SUMMARY_SELECT_DATE_FROM':
      return Object.assign({}, state, { selectOffersFrom: action.payload })
    case action.type === 'BOOKING_SUMMARY_SELECT_DATE_TO':
      return Object.assign({}, state, { selectOffersTo: action.payload })
    default:
      return state
  }
}
