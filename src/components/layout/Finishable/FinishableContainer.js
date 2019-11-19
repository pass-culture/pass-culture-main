import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import getIsBooked from '../../../helpers/getIsBooked'
import { selectBookingByRouterMatch } from '../../../selectors/data/bookingsSelectors'
import { selectIsNotBookableByRouterMatch } from '../../../selectors/isNotBookableSelector'
import Finishable from './Finishable'

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
