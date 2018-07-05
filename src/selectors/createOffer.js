import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.offers,
  (state, eventOccurenceId) => eventOccurenceId,
  (offers, eventOccurenceId) => offers.find(offer =>
    offer.eventOccurenceId === eventOccurenceId)
)
