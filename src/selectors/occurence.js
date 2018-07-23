import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, occurence) => occurence,
  occurence => {
    return occurence && Object.assign({},
      {
        beginningDatetime: moment(get(occurence, 'beginningDatetime'))
          .add(1, 'day')
          .toISOString(),
        endDatetime: moment(get(occurence, 'endDatetime'))
          .add(1, 'day')
          .toISOString(),
      },
      occurence
    )
  }
)(
  (state, occurence) => get(occurence, 'id') || ''
)
