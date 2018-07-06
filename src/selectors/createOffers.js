import { createSelector } from 'reselect'

import occurencesSelector from './occurences'

export default () => createSelector(
  state => state.data.offers,
  occurencesSelector,
  (offers, occurences) => {
    return offers.filter(offer => {
      return occurences.some(occurence => offer.eventOccurenceId === occurence.id)
    })
  }
)
