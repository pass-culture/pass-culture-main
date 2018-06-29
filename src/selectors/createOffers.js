import { createSelector } from 'reselect'

import createOccurencesSelector from './createOccurences'

export default (occurencesSelector=createOccurencesSelector()) => createSelector(
  state => state.data.offers,
  occurencesSelector,
  (offers, occurences) => {
    return offers.filter(offer => {
      return occurences.some(occurence => offer.eventOccurenceId === occurence.id)
    })
  }
)
