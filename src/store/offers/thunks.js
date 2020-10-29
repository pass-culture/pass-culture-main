import * as pcapi from 'repository/pcapi/pcapi'
import { setStocks, setVenues } from 'store/reducers/data'

import { setOffers } from './actions'

export const setAllVenueOffersActivate = venueId => {
  return dispatch => {
    return pcapi.setAllVenueOffersActivate(venueId).then(offersRecap => {
      dispatch(setOffersRecap(offersRecap))
    })
  }
}

export const setAllVenueOffersInactivate = venueId => {
  return dispatch => {
    return pcapi.setAllVenueOffersInactivate(venueId).then(offersRecap => {
      dispatch(setOffersRecap(offersRecap))
    })
  }
}

export const loadOffer = offerId => {
  return dispatch => {
    return pcapi.loadOffer(offerId).then(rawOffer => {
      const { stocks, venue, ...offer } = rawOffer
      dispatch(setOffers([offer]))
      dispatch(setStocks(stocks))
      dispatch(setVenues([venue]))
    })
  }
}

export const loadOffers = filters => {
  return dispatch => {
    return pcapi
      .loadFilteredOffers(filters)
      .then(({ offers: offersRecap, page, page_count: pageCount, total_count: offersCount }) => {
        dispatch(setOffersRecap(offersRecap))
        return { page, pageCount, offersCount }
      })
  }
}

export const setOffersRecap = offersRecap => {
  return dispatch => {
    const { offers, stocks, venues } = offersRecapNormalizer(offersRecap)
    dispatch(setOffers(offers))
    dispatch(setStocks(stocks))
    dispatch(setVenues(venues))
  }
}

const offersRecapNormalizer = offersRecap => {
  const stocks = []
  const venues = []

  const offers = offersRecap.map(offer => {
    const { stocks: offerStocks, venue: offerVenue, ...offerStrippedOfStocksAndVenue } = offer
    stocks.push(...offerStocks)
    venues.push(offerVenue)

    return offerStrippedOfStocksAndVenue
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
