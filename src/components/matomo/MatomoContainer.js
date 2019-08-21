import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'
import { withRouter } from 'react-router'

import Matomo from './Matomo'

export const mapStateToProps = state => {
  let id
  let canBookFreeOffers
  const user = selectCurrentUser(state)
  if (user) {
    id = user.id
    canBookFreeOffers = user.canBookFreeOffers
  }

  return {
    id,
    canBookFreeOffers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
