import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoControls from './VersoControls'
import { selectBookingByRouterMatch } from '../../../../redux/selectors/data/bookingsSelectors'
import getIsBooked from '../../../../utils/getIsBooked'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const booking = selectBookingByRouterMatch(state, match)
  const isBooked = getIsBooked(booking)

  return {
    isBooked,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControls)
