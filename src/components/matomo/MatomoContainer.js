import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from '../../selectors/data/usersSelectors'
import { withRouter } from 'react-router'

import Matomo from './Matomo'
import { selectUserGeolocation } from '../../selectors/geolocationSelectors'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  const userId = user ? user.id : 'ANONYMOUS'
  const coordinates = selectUserGeolocation(state)

  return {
    userId,
    coordinates,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
