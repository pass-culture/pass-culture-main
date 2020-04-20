import { createDataReducer } from 'redux-saga-data'

const data = createDataReducer({
  bookings: [],
  events: [],
  features: [],
  mediations: [],
  offers: [],
  offerers: [],
  providers: [],
  stocks: [],
  things: [],
  types: [],
  users: [],
  userOfferers: [],
  venues: [],
  "venue-types": [],
  venueProviders: [],
})

export default data
