import { createDataReducer } from 'redux-saga-data'

const SET_STOCKS = 'SET_STOCKS'
const SET_VENUES = 'SET_VENUES'

export const initialState = {
  bookings: [],
  events: [],
  features: [],
  mediations: [],
  offerers: [],
  providers: [],
  stocks: [],
  things: [],
  types: [],
  users: [],
  userOfferers: [],
  venues: [],
  'venue-types': [],
  venueProviders: [],
}

const dataReducer = createDataReducer(initialState)

export const setStocks = stocks => ({
  stocks,
  type: SET_STOCKS,
})

export const setVenues = venues => ({
  venues,
  type: SET_VENUES,
})

const dataAndOffersRecapReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_VENUES:
      return { ...state, ...{ venues: action.venues } }
    case SET_STOCKS:
      return { ...state, ...{ stocks: action.stocks } }
    case 'GET_DESK_BOOKINGS':
      return { ...state, ...{ deskBookings: [action.payload] } }
    default:
      return dataReducer(state, action)
  }
}

export default dataAndOffersRecapReducer
