import moment from 'moment'
import { createSelector } from 'reselect'

import createOccurencesSelector from './createOccurences'

export default () => createSelector(
  createOccurencesSelector(),
  occurences =>
    occurences && occurences.map(o =>
      moment(o.beginningDatetime)
    ).reduce((max, d) => max &&
      max.isAfter(d) ? max : d, null
    )
)
