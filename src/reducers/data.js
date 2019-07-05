import { createDataReducer } from 'redux-saga-data'

const data = createDataReducer({
  bookings: [],
  events: [],
  mediations: [],
  offers: [],
  offerers: [],
  pendingOfferers: [],
  providers: [],
  stocks: [],
  things: [],
  types: [],
  users: [],
  userOfferers: [],
  venues: [],
  venueProviders: [],
})

export default data
