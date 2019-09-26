import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { selectCurrentUser } from 'with-react-redux-login'
import { compose } from 'redux'

import Header from './Header'

export const mapStateToProps = state => {
  const { data } = state
  const user = selectCurrentUser(state)
  const { publicName: name } = user
  const { offerers } = data

  return {
    name,
    offerers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Header)
