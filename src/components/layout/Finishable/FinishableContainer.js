import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Finishable from './Finishable'
import { selectBookingByRouterMatch } from '../../../selectors/data/bookingsSelectors'
import getIsBooked from '../../../helpers/getIsBooked'
import { selectIsNotBookableByRouterMatch } from '../../../selectors/data/bookablesSelectors'

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
