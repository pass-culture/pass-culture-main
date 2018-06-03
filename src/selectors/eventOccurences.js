import moment from 'moment'
import { createSelector } from 'reselect'

import { DELETE } from '../utils/config'




export default createSelector(
  state => state.form.eventOccurencesById,
  (state, ownProps) => ownProps.occurences,
  (formEventOccurencesById, occurences) => {

    // by default it is directly the props occurences
    let filteredOccurences = occurences

    if (formEventOccurencesById) {
      filteredOccurences = []
      // remove the occurences that was deleted inside the form
      // and add the new created ones
      const formEventOccurences = Object.values(formEventOccurencesById)
      for (let occurence of occurences) {
        const index = formEventOccurences.findIndex(formEventOccurence =>
          (formEventOccurence && formEventOccurence.id) === occurence.id)
        if (index > -1) {
          const formEventOccurence = formEventOccurences[index]
          if (formEventOccurence.DELETE === DELETE) {
            delete formEventOccurences[index]
          } else {
            filteredOccurences.push(formEventOccurence)
          }
        } else {
          filteredOccurences.push(occurence)
        }
      }
      // add the new ones
      formEventOccurences.forEach(formEventOccurence =>
        filteredOccurences.push(formEventOccurence))
    }

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
