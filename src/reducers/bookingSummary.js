const initialState = {
  isFilterByDigitalVenues: false,
  selectedVenue: '',
}

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE':
      if (action.payload === true) {
        return Object.assign({}, state, {
          selectedVenue: '',
          isFilterByDigitalVenues: action.payload,
        })
      }
      return Object.assign({}, state, {
        selectedVenue: '',
        isFilterByDigitalVenues: action.payload,
      })
    case 'BOOKING_SUMMARY_SELECT_VENUE':
      return Object.assign({}, state, {
        selectedVenue: action.payload,
      })
    default:
      return state
  }
}
