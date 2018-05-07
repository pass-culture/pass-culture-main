import { createSelector } from 'reselect'

import selectOffersWithSource from './offersWithSource'

export default createSelector(
  selectOffersWithSource,
  offers => {
    if (!offers) {
      return
    }
    const sortOffers = [...offers]
    // youngest are at the top of the list
    sortOffers.sort((o1, o2) => o2.id - o1.id)
    return sortOffers
  }
)
