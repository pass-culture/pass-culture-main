import { connect } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'

import Signup from './Signup'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(Signup)
