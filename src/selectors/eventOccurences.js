import { createSelector } from 'reselect'

import { DELETE } from '../utils/config'

export default createSelector(
  state => state.form.eventOccurencesById,
  (state, ownProps) => ownProps.occurences,
  (eventOccurencesById, occurences) => {
    if (!eventOccurencesById) {
      return occurences
    }
    const filteredOccurences = []
    const deletedEventOccurenceIds = Object.values(eventOccurencesById)
      .filter(eo => eo.DELETE === DELETE)
      .map(eo => eo.id)
    for (let occurence of occurences) {
      const index = deletedEventOccurenceIds.findIndex(id => id === occurence.id)
      if (index > -1) {
        delete deletedEventOccurenceIds[index]
      } else {
        filteredOccurences.push(occurence)
      }
    }
    return filteredOccurences
  }
)
