import moment from 'moment'
import { createSelector } from 'reselect'

import createOccurencesSelector from './createOccurences'

const occurencesSelector = createOccurencesSelector()

export default () => createSelector(
  occurencesSelector,
  occurences =>
    occurences && occurences.map(o =>
      moment(o.beginningDatetime)
    ).reduce((max, d) => max &&
      max.isAfter(d) ? max : d, null
    )
)
