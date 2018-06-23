import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.eventOccurences,
  (state, ownProps) => get(ownProps, 'occasion.eventId'),
  (eventOccurences, eventId) => {
    if (!eventOccurences) {
      return
    }

    let filteredOccurences
    if (eventId) {
      filteredOccurences = eventOccurences.filter(eventOccurence =>
        eventOccurence.eventId === eventId)
    } else {
      filteredOccurences = [...eventOccurences]
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
