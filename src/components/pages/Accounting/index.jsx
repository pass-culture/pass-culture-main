import get from 'lodash.get'
import { withPagination } from 'pass-culture-shared'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import RawAccounting from './RawAccounting'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import selectOffererById from '../../../selectors/selectOffererById'
import { mapApiToWindow, windowToApiQuery } from '../../../utils/pagination'

const mapStateToProps = (state, ownProps) => {
  const offererId = get(
    ownProps,
    `pagination.windowQuery.${mapApiToWindow.offererId}`
  )

  return {
    bookings: state.data.bookings,
    offerer: selectOffererById(state, offererId),
    offerers: state.data.offerers,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withRouter,
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
