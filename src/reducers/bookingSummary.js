const initialState = {
  isFilterByDigitalVenues:false,
  selectedVenue:"",
  selectedOffer:"",
  selectOffersSince:new Date(2018, 1, 1),
}

export default (state = initialState, action={}) => {

  switch(action.type){
    case 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE':
      if (action.payload === true){
        return Object.assign({}, state, {selectedOffer: "", selectedVenue: "", isFilterByDigitalVenues: action.payload })
      }
      return Object.assign({}, state, { selectedOffer: "", selectedVenue: "", isFilterByDigitalVenues: action.payload })
    case 'BOOKING_SUMMARY_SELECT_VENUE':
      return Object.assign({}, state, { selectedOffer: "", selectedVenue: action.payload })
    case 'BOOKING_SUMMARY_SELECT_OFFER':
      return Object.assign({}, state, { selectedOffer: action.payload })
    case 'BOOKING_SUMMARY_SELECT_DATE':
      return Object.assign({}, state, { selectOffersSince: action.payload })
    default:
      return state
  }
}
