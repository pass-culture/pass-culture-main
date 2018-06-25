import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

const createOccurencesSelect = () => createSelector(
  state => get(state, 'data.eventOccurences', []),
  (state, params) => params,
  (eventOccurences, {venueId, eventId}) => {
    return eventOccurences
      .filter(o => {
        o.venueId === venueId &&
        o.eventId === eventId
      })
      .map(o => Object.assign(o, {beginningDatetimeMoment: moment(o.beginningDatetime)}))
      .sort((o1,o2) =>
      o1.beginningDatetimeMoment - o2.beginningDatetimeMoment)
  }
)

export default createOccurencesSelect
