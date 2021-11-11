import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from '../../redux/selectors/currentUserSelector'
import { withRouter } from 'react-router'

import Matomo from './Matomo'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  const userId = user ? user.id : 'ANONYMOUS'

  return {
    userId,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
