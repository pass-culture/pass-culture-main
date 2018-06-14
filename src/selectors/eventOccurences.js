import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'


export default createSelector(
  state => state.data.eventOccurences,
  (state, ownProps) => get(ownProps, 'occasion.id'),
  (eventOccurences, eventId) => {
    if (!eventOccurences || !eventId) {
      return
    }

    // filter
    const filteredOccurences = eventOccurences.filter(eo =>
      eo.eventId === eventId)

    // sort by dates
    if (filteredOccurences) {
      filteredOccurences.forEach(o => {
        o.beginningDatetimeMoment = moment(o.beginningDatetime)
      })
      filteredOccurences.sort((o1,o2) =>
        o1.beginningDatetimeMoment - o2.beginningDatetimeMoment)
    }

    // return
    return filteredOccurences
  }
)
