import moment from 'moment'
import { createSelector } from 'reselect'

const createOccurencesSelector = () => createSelector(
  state => state.data.eventOccurences,
  (state, venueId) => venueId,
  (state, venueId, eventId) => eventId,
  (eventOccurences, venueId, eventId) => {
    if (venueId)
      eventOccurences = eventOccurences.filter(o => o.venueId === venueId)
    if (eventId)
      eventOccurences = eventOccurences.filter(o => o.eventId === eventId)
    return eventOccurences
      .map(o => Object.assign(o, {
        beginningDatetimeMoment: moment(o.beginningDatetime),
        endDatetimeMoment: moment(o.endDatetime)
      }))
      .sort((o1,o2) =>
        o2.beginningDatetimeMoment - o1.beginningDatetimeMoment
      )
  }
)

export default createOccurencesSelector
