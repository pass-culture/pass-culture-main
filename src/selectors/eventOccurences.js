import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import { getElementsWithoutDeletedFormValues } from '../utils/form'
import { DELETE } from '../utils/config'


export default createSelector(
  (state, ownProps) => get(ownProps, 'occasion.occurences'),
  state => state.form.eventOccurencesById,
  (occurences, formEventOccurencesById) => {

    // by default it is directly the props occurences
    let filteredOccurences = occurences

    if (formEventOccurencesById) {
      filteredOccurences = getElementsWithoutDeletedFormValues(
        occurences || [],
        Object.values(formEventOccurencesById)
      )
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
