import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Header from './Header'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  return {
    isUserAdmin: user && user.isAdmin,
  }
}

export default connect(mapStateToProps)(Header)
