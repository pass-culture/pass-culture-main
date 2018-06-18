import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.eventOccurences,
  eventOccurences => {
    if (!eventOccurences) {
      return
    }

    // clone
    const filteredOccurences = [...eventOccurences].map(eo =>
      Object.assign({}, eo))

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
