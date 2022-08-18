import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'

import Header from './Header'

const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  return {
    isUserAdmin: user && user.isAdmin,
  }
}

export default connect(mapStateToProps)(Header)
