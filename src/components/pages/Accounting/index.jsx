import get from 'lodash.get'
import { withPagination } from 'pass-culture-shared'
import { compose } from 'redux'
import { connect } from 'react-redux'

import RawAccounting from './RawAccounting'
import { withRequiredLogin } from '../../hocs'
import selectOffererById from '../../../selectors/selectOffererById'
import { mapApiToWindow, windowToApiQuery } from '../../../utils/pagination'

const mapStateToProps = (state, ownProps) => {
  const offererId = get(ownProps, `pagination.windowQuery.${mapApiToWindow.offererId}`)

  return {
    bookings: state.data.bookings,
    offerer: selectOffererById(state, offererId),
    offerers: state.data.offerers,
  }
}

export default compose(
  withRequiredLogin,
  withPagination({
    dataKey: 'bookings',
    defaultWindowQuery: {
      [mapApiToWindow.keywords]: null,
      [mapApiToWindow.offererId]: null,
      [mapApiToWindow.venueId]: null,
      orderBy: 'booking.id+desc',
    },
    windowToApiQuery,
  }),
  connect(mapStateToProps)
)(RawAccounting)
