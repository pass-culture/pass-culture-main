import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectSelectedVenueId from './selectedVenueId'

const createSelectOccurences = () => createSelector(
  state => state.data.eventOccurences,
  selectSelectedVenueId,
  (state, ownProps) => get(ownProps, 'occasion.eventId'),
  (eventOccurences, selectedVenueId, eventId) => {
    if (!eventOccurences) {
      return
    }

    let filteredOccurences = [...eventOccurences]

    if (selectedVenueId) {
      filteredOccurences = filteredOccurences.filter(o =>
        o.venueId === selectedVenueId)
    }
    if (eventId) {
      filteredOccurences = filteredOccurences.filter(eventOccurence =>
        eventOccurence.eventId === eventId)
    }

    // clone
    filteredOccurences = filteredOccurences.map(eo =>
      Object.assign({}, eo))

    // sort by dates
    filteredOccurences.forEach(o => {
      o.beginningDatetimeMoment = moment(o.beginningDatetime)
    })
    filteredOccurences.sort((o1,o2) =>
      o1.beginningDatetimeMoment - o2.beginningDatetimeMoment)

    // return
    return filteredOccurences
  }
)

export default createSelectOccurences

export const selectCurrentOccurences = createSelectOccurences()
