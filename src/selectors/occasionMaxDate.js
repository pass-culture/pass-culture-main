import moment from 'moment'
import { createSelector } from 'reselect'

export default selectCurrentOccurences => createSelector(
  selectCurrentOccurences,
  currentOccurences =>
    currentOccurences && currentOccurences.map(o =>
        moment(o.beginningDatetime)
      ).reduce((max, d) => max &&
        max.isAfter(d) ? max : d, null
      )
)
