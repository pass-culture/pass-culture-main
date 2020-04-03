import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from '../../selectors/data/usersSelectors'
import { withRouter } from 'react-router'
import withTracking from '../hocs/withTracking'

import Matomo from './Matomo'
import { selectUserGeolocation } from '../../selectors/geolocationSelectors'

export const mapStateToProps = (state, ownProps) => {
  const user = selectCurrentUser(state)
  const userId = user ? user.id : 'ANONYMOUS'
  const coordinates = selectUserGeolocation(state)

  return {
    userId,
    coordinates,
    tracking: ownProps.tracking,
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(mapStateToProps)
)(Matomo)
