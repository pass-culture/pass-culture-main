import * as pcapi from 'repository/pcapi/pcapi'
import { setMediations, setStocks, setVenues } from 'store/reducers/data'

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
      dispatch(setOffersRecap([rawOffer]))
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
    const { mediations, offers, stocks, venues } = offersRecapNormalizer(offersRecap)
    dispatch(setMediations(mediations))
    dispatch(setOffers(offers))
    dispatch(setStocks(stocks))
    dispatch(setVenues(venues))
  }
}

const offersRecapNormalizer = offersRecap => {
  const mediations = []
  const stocks = []
  const venues = []

  const offers = offersRecap.map(rawOffer => {
    const { stocks: offerStocks, venue: offerVenue, ...offerStrippedOfStocksAndVenue } = rawOffer

    let flatOffer = offerStrippedOfStocksAndVenue
    if (rawOffer.mediations) {
      const {
        mediations: offerMediations,
        ...offerStrippedOfMediations
      } = offerStrippedOfStocksAndVenue
      mediations.push(...offerMediations)
      flatOffer = offerStrippedOfMediations
    }

    stocks.push(...offerStocks)
    venues.push(offerVenue)

    return flatOffer
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
    mediations: mediations,
    offers: offers,
    stocks: stocks,
    venues: uniqueVenues,
  }
}
