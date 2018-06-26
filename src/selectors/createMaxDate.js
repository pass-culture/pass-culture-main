import moment from 'moment'
import { createSelector } from 'reselect'

export default occurencesSelector => createSelector(
  occurencesSelector,
  occurences =>
    occurences && occurences.map(o =>
      moment(o.beginningDatetime)
    ).reduce((max, d) => max &&
      max.isAfter(d) ? max : d, null
    )
)
