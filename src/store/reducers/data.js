import { createDataReducer } from 'redux-saga-data'

const GET_DESK_BOOKINGS = 'GET_DESK_BOOKINGS'
const SET_MEDIATIONS = 'SET_MEDIATIONS'
const SET_STOCKS = 'SET_STOCKS'
const SET_VENUES = 'SET_VENUES'
const SET_VENUE_PROVIDERS = 'SET_VENUE_PROVIDERS'

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

export const setMediations = mediations => ({
  mediations,
  type: SET_MEDIATIONS,
})

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
    case GET_DESK_BOOKINGS:
      return { ...state, ...{ deskBookings: [action.payload] } }
    case SET_MEDIATIONS:
      return { ...state, ...{ mediations: action.mediations } }
    case SET_STOCKS:
      return { ...state, ...{ stocks: action.stocks } }
    case SET_VENUES:
      return { ...state, ...{ venues: action.venues } }
    case SET_VENUE_PROVIDERS:
      return { ...state, ...{ venueProviders: [action.payload] } }
    default:
      return dataReducer(state, action)
  }
}

export default dataAndOffersRecapReducer
