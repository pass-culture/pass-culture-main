import moment from 'moment'
import { createSelector } from 'reselect'

export default (
  selectOccurences
) => createSelector(
  selectOccurences,
  occurences =>
    occurences && occurences.map(o =>
      moment(o.beginningDatetime)
    ).reduce((max, d) => max &&
      max.isAfter(d) ? max : d, null
    )
)
