import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, occurence) => occurence,
  occurence => {
    return occurence && Object.assign({},
      occurence,
      {
        beginningDatetime: moment(get(occurence, 'beginningDatetime'))
          .toISOString(),
        endDatetime: moment(get(occurence, 'endDatetime'))
          .toISOString(),
      }
    )
  }
)(
  (state, occurence) => get(occurence, 'id') || ''
)
