import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Finishable from './Finishable'
import selectIsNotBookableByRouterMatch from '../../../selectors/selectIsNotBookableByRouterMatch'
import { selectBookingByRouterMatch } from '../../../selectors/data/bookingsSelector'
import getIsBooked from '../../../helpers/getIsBooked'

const mapStateToProps = (state, { match }) => {
  const booking = selectBookingByRouterMatch(state, match)
  const isNotBookable = selectIsNotBookableByRouterMatch(state, match) && !getIsBooked(booking)

  return {
    isNotBookable,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
