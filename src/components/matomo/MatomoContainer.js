import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from '../../selectors/data/usersSelectors'
import { withRouter } from 'react-router'

import Matomo from './Matomo'
import { selectUserGeolocation } from '../../selectors/geolocationSelectors'

export const mapStateToProps = (state, ownProps) => {
  const user = selectCurrentUser(state)
  let userId = user ? user.id : 'ANONYMOUS'
  const coordinates = selectUserGeolocation(state)
  if (coordinates.latitude && coordinates.longitude) {
    ownProps.tracking.trackEvent({ action: 'activatedGeolocation', name: userId })
  }
  return {
    userId,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
