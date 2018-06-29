import moment from 'moment'
import { createSelector } from 'reselect'

import createOccurencesSelector from './createOccurences'

export default (occurencesSelector=createOccurencesSelector()) => createSelector(
  occurencesSelector,
  occurences => {
    return occurences
      .reduce((max, d) => max &&
        max.isAfter(d.beginningDatetimeMoment) ? max : d.beginningDatetimeMoment, null
      )
  }
)
