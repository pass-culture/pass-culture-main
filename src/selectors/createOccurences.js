import moment from 'moment'
import { createSelector } from 'reselect'

const createOccurencesSelector = () => createSelector(
  state => state.data.eventOccurences,
  (state, venueId) => venueId,
  (state, venueId, eventId) => eventId,
  (eventOccurences, venueId, eventId) => {
    return eventOccurences
      .filter(o =>
        o.venueId === venueId &&
        o.eventId === eventId
      )
      .map(o => Object.assign(o, {beginningDatetimeMoment: moment(o.beginningDatetime),
                                 endDatetimeMoment: moment(o.endDatetime)}))
      .sort((o1,o2) =>
      o1.beginningDatetimeMoment - o2.beginningDatetimeMoment)
  }
)

export default createOccurencesSelector
