import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoControls from './VersoControls'
import selectBookingByRouterMatch from '../../../../selectors/selectBookingByRouterMatch'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const booking = selectBookingByRouterMatch(state, match)
  const showCancelView = booking && !booking.isCancelled
  return {
    showCancelView,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControls)
