import { createDataReducer } from 'redux-saga-data'

const initialState = {
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
  'venue-types': [],
  venueProviders: [],
}

const dataReducer = createDataReducer(initialState)

const paginatedOffersRecapNormalizer = offersRecap => {
  const stocks = []
  const venues = []

  const offers = offersRecap.map(offer => {
    const { stocks: offerStocks, venue: offerVenue, ...offerWithoutStocksAndVenue } = offer
    stocks.push(...offerStocks)
    venues.push(offerVenue)

    return offerWithoutStocksAndVenue
  })

  const uniqueVenues = venues.reduce((accumulator, venue) => {
    const isVenueAlreadyAccumulated = accumulator.some(
      accumulatedVenue => accumulatedVenue.id === venue.id
    )

    if (!isVenueAlreadyAccumulated) {
      accumulator.push(venue)
    }

    return accumulator
  }, [])

  return {
    offers: offers,
    stocks: stocks,
    venues: uniqueVenues,
  }
}

const dataAndOffersRecapReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'GET_PAGINATED_OFFERS':
      return { ...state, ...paginatedOffersRecapNormalizer(action.payload) }
    default:
      return dataReducer(state, action)
  }
}

export default dataAndOffersRecapReducer
