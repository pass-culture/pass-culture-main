import Header from './Header'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/user/selectors'

export const mapStateToProps = state => {
  const user = selectCurrentUser(state)
  return {
    isUserAdmin: user && user.isAdmin,
  }
}

export default connect(mapStateToProps)(Header)
