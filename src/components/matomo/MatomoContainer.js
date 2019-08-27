import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'
import { withRouter } from 'react-router'

import Matomo from './Matomo'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  let userId
  if (user) {
    userId = user.id
  } else {
    userId = 'ANONYMOUS'
  }

  return {
    userId,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
