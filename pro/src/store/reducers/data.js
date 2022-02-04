import { createDataReducer } from 'redux-saga-data'

const GET_DESK_BOOKINGS = 'GET_DESK_BOOKINGS'
const SET_MEDIATIONS = 'SET_MEDIATIONS'
const SET_STOCKS = 'SET_STOCKS'
const SET_VENUES = 'SET_VENUES'
const SET_USERS = 'SET_USERS'
const UPDATE_USER = 'UPDATE_USER'

export const initialState = {
  bookings: [],
  events: [],
  features: [],
  mediations: [],
  offerers: [],
  stocks: [],
  things: [],
  types: [],
  users: [],
  userOfferers: [],
  venues: [],
  'venue-types': [],
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

export const setUsers = users => ({
  users,
  type: SET_USERS,
})

export const updateUser = userData => ({
  userData,
  type: UPDATE_USER,
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
    case SET_USERS:
      return { ...state, ...{ users: action.users } }
    case UPDATE_USER: {
      const currentUser = state.users[0]
      return {
        ...state,
        ...{ users: [{ ...currentUser, ...action.userData }] },
      }
    }
    default:
      return dataReducer(state, action)
  }
}

export default dataAndOffersRecapReducer
