import groupby from 'lodash.groupby'
import { createSelector } from 'reselect'

import selectOffersWithSource from './offersWithSource'

export default createSelector(
  selectOffersWithSource,
  offers => {
    if (!offers) {
      return
    }
    const sortedOffers = [...offers]
    // youngest are at the top of the list
    sortedOffers.sort((o1, o2) => o2.id - o1.id)
    return Object.values(groupby(sortedOffers, o => o.source.id))
  }
)
